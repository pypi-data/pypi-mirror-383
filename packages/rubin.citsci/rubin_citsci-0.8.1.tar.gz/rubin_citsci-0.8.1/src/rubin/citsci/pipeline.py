import csv, uuid, os, shutil, json, logging, urllib.request, base64, re, requests
from datetime import datetime, timezone, timedelta
from IPython.display import display
from importlib.metadata import version
import google.cloud.storage as storage
import panoptes_client
from panoptes_client import Project, SubjectSet, Classification, Workflow

class CitSciPipeline:
    """
        Important: DO NOT MODIFY!

        Developed for the LSST Rubin Science Platform Notebook Aspect
        This product includes software developed by the LSST Project
        (https://www.lsst.org).
        See the COPYRIGHT file at the top-level directory of this distribution
        for details of code ownership.

        This program is free software: you can redistribute, but DO NOT modify
        it under the terms of the Non-Commercial No-Derivatives International
        (CC BY-NC-ND 4.0) License as published by the Creative Commons, either
        version 4 of the License, or (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        Creative Commons NC-ND License for more details.
        _______________________________________________________________________

        The purpose of this class is to act as a touchpoint between the Rubin
        Science Platform Notebook Aspect and the service that exports notebook
        user data from their notebook filesystem to their Zooniverse project as
        a new subject set.

        If necessary, Zooniverse project creation is also available as a method.
    """
    
    def __init__(self):
        """
            Sets defaults.
        """

        os.environ[base64.b64decode("R09PR0xFX0FQUExJQ0FUSU9OX0NSRURFTlRJQUxT").decode("ascii")] = self.__get_gcp_location()
        self.vendor_batch_id = 0
        self.project_id = -1
        self.guid = ""
        self.manifest_url = ""
        self.edc_response = ""
        self.step = 0
        self.email = ""
        self.project = None
        self.client = None
        if os.getenv("CITSCI_PIPELINE_DEV_MODE") == "1" or (os.getenv("CITSCI_PIPELINE_DEV_MODE") is not None and os.getenv("CITSCI_PIPELINE_DEV_MODE").lower() == "true") :
            self.dev_mode_url = "-dev"
            print("Development mode enabled.")
        else:
            self.dev_mode_url = ""

    def project_sanity_check(self):
        if self.project is None or self.project_id == -1:
            print("No project has been selected! Either re-run the login cell to select the project you would like to send data to or run the cell that create a project from the Rubin template!")
            return False
        else:
            return True

    def create_new_project_from_template(self, project_id=21302):
        """
            This method will create a new project under the authenticated user's account
            based on the provided Zooniverse project ID. If no project template ID is
            provided then a new project will be created from a Rubin test project 
            template.

            Must be authenticated into the Zooniverse API or an exception will occur.

            Returns an instance of a Zooniverse project.
        """

        if self.project is not None:
            print("\n### WARNING - You have already select a project to send data to! Please only proceed if you intend to create a new project and would like to set this new project as the target for sending new data to.\n")
        print("\n### WARNING - You are about to create a new project based on a predefined Rubin template project!\n")
        response = input("Are you sure you would like to create a new project? (type out 'yes')")
        if response.lower() == "yes":
            project_template = Project.find(id=project_id)
            self.project = project_template.copy()
            self.project.save()
            self.project_id = self.project.id
            return self.project
        else:
            print("\nNew project creation has been cancelled.")
            return

    def login_to_zooniverse(self, email):
        """
            Email address validation occurs before the login prompt is called and also
            checks if the latest version of this package is installed.
        """

        self.__check_package_version()
        
        valid_email = self.__validate_email_address(email)

        if(valid_email):
            print("Loading and running utilities to establish a link with Zooniverse")
            print("Enter your Zooniverse username followed by password below")  
            self.email = email
            self.client = panoptes_client.Panoptes.connect(login="interactive")
            if self.client.logged_in is True:
                print("You now are logged in to the Zooniverse platform.")
                self.__log_slug_names()
            else:
                print("Please supply a valid username and password.")

            return
        else:
            print("Invalid email address! Please check the email address you provided and ensure it is correct.")
        return
    
    def list_workflows(self):
        """
            If the user has logged into the Zooniverse platform via the login_to_zooniverse()
            function and selected a project, then this cell will list all active workflows for
            the selected project.
        """

        if self.project is None:
            print("Please log in first using login_to_zooniverse() first before attempting to retrieve workflows.")
            return
        
        active_workflows = self.project.raw["links"]["active_workflows"]
        if len(active_workflows) > 0:
            print("\n*==* Your Workflows *==*\n")
            for workflow in active_workflows:
                display_name = Workflow.find(workflow).raw["display_name"]
                print(f"Workflow ID: {workflow} - Display Name: {display_name}")
            print("\n*==========================*\n")
        else:
            print("There are no active workflows for the project you have selected.")
        return
    
    def __log_slug_names(self):
        projects = self.client.get(f"/projects?owner={self.client.username}")
        slugnames = []
        has_projects = False

        print("\n*==* Your Project Slugs *==*\n")
        for proj in projects:
            if type(proj) is dict:
                for p in proj["projects"]:
                    has_projects = True
                    slugnames.append(p["slug"])
                    print(p["slug"])
        print("\n*==========================*\n")

        if has_projects == True:
            slug_name = input("Which project would you like to connect to? (copy & paste the slug name here)?")
            if slug_name in slugnames:
                self.project = Project.find(slug=slug_name)
                self.project_id = self.project.id
                print(f"Current project set to: {slug_name}")
            else:
                print("\n### Invalid project slug name! Please re-run this cell and copy-paste a slug name from the provided list.")
        else:
            print("You do not have any projects on the Zooniverse platform. Please run the cell that creates a new project based on the project template.")
        return
    
    def __check_package_version(self):
        try:
            installed_version = version('rubin.citsci')
            res = requests.get('https://pypi.org/simple/rubin-citsci/', headers = {"Accept": "application/vnd.pypi.simple.v1+json"})
            res_json = json.loads(res.content.decode('utf-8'))
            latest_version = res_json["versions"][-1]

            if (installed_version == latest_version) is False:
                print("WARNING! : You currently have v" + installed_version + " of this package installed, but v" + latest_version + " is available.")
                print("To install the latest version, open up a terminal tab and run the following command:")
                print("    pip install --upgrade --force-reinstall rubin.citsci")
                print("After the upgrade installation has finished, please restart the kernel for the changes to take effect.")
                print("Failing to keep the rubin.citsci package up-to-date will likely cause the following cells to fail.")
        except Exception as e:
                print("ERROR! : An error occurred while attempting to validate that the latest version of the rubin.citsci package is installed. Please notify the EPO citizen science team that this error message has occurred!")
        return
    
    def __validate_email_address(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if re.fullmatch(regex, email):
            return True
        else:
            return False
    
    def create_project(self, name, description, make_active_project=False):
        """
            Assuming you have a Zooniverse account and have used the login_to_zooniverse()
            method to log in, this method will create a new project for you with the
            following settings:

                Primary Language: U.S. English
                Private: False

            And CitizenSciencePipelineError exception is thrown if the 'name' or 'description' 
            name arguments are not specified.

            Returns a dict with the newly created project details.
        """
        
        if name is None or description is None:
            raise CitizenSciencePipelineError("Both the 'project_name' and 'description' arguments are required.") 

        if self.project is not None:
            print("\n### WARNING - You have already select a project to send data to! Please only proceed if you intend to create a new project and would like to set this new project as the target for sending new data to.\n")
        print("\n### WARNING - You are about to create a new project!\n")
        response = input("Are you sure you would like to create a new project? (type out 'yes')")
        if response.lower() == "yes":
            project = Project()
            project.name = name
            project.display_name = name
            project.description = description
            project.primary_language = "en-us"
            project.private = False
            project.save()

            if make_active_project is not None and make_active_project is True:
                self.project = project.slug
                self.project_id = project.project.id

            return project.__dict__
        else:
            print("\nNew project creation has been cancelled.")
            return

    def write_manifest_file(self, manifest, batch_dir):
        """
            Takes an array of dicts in Zooniverse canonical format and writes
            a CSV manifest file to the Notebook Aspect's filesystem in the 
            specified batch directory.

            Returns the relative path to the manifest.csv
        """   
        
        if self.project_sanity_check() is False:
            print("Please create or specify a Zooniverse project before attempting to write a manifest file.")
            return
        manifest_filename = 'manifest.csv'
        with open(batch_dir + manifest_filename, 'w', newline='') as csvfile:
            fieldnames = list(manifest[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for cutout in manifest:
                writer.writerow(cutout)

        manifest_path = f"{batch_dir}{manifest_filename}"
        print(f"The manifest CSV file can be found at the following relative path: {manifest_path}")

        return manifest_path
    
    def clean_up_unused_subject_set(self):
        """
            This method is used when a subject set was created as part of the 
            data transfer process, but for some reason the process errored out
            and the empty subject set now needs to be cleaned up (deleted) so
            that unused subject sets do not clutter the target Zooniverse
            project.

            This method will quietly fail if there was no subject set found or
            if the login method hasn't been executed yet.
        """

        self.log_step("Cleaning up unused subject set on the Zooniverse platform, vendor_batch_id : " + str(self.vendor_batch_id))

        try:
            subject_set = SubjectSet.find(str(self.vendor_batch_id))

            if subject_set.id == self.vendor_batch_id:
                subject_set.delete()

        except:
            pass
            # display(f"** Warning: Failed to find the subject set with id: {str(self.vendor_batch_id)}- perhaps it's been deleted?.")
        return

    def __send_zooniverse_manifest(self):
        """
            This function is called as part of the send_image_data()  workflow and should
            not be accessed publicly as unexpected results will occur.
        """

        self.log_step("Sending the manifest URL to Zooniverse")
        display("** Information: subject_set.id: " + str(self.vendor_batch_id) + "; manifest: " + self.manifest_url);

        payload = {"subject_set_imports": {"source_url": self.manifest_url, "links": {"subject_set": str(self.vendor_batch_id)}}}
        json_response, etag = self.client.post(path='/subject_set_imports', json=payload)
        return

    def __create_new_subject_set(self, name):
        """
            This function is called as part of the send_image_data() workflow and should
            not be accessed publicly as unexpected results will occur.
        """

        self.log_step("Creating a new Zooniverse subject set")

        # Create a new subject set
        subject_set = panoptes_client.SubjectSet()
        subject_set.links.project = self.project

        # Give the subject set a display name (that will only be visible to you on the Zooniverse platform)
        subject_set.display_name = name 
        subject_set.save()
        self.project.reload()
        self.vendor_batch_id = subject_set.id
        return self.vendor_batch_id

    def check_status(self):
        """
            This method will check whether or not the manifest file has been moved to the public
            storage bucket - which occurs at the last step of the process of transferring the
            new data to the target Zooniverse.

            This method was implemented because the processing time for sending the maximum 
            number of objects to the Zooniverse can be > 2 minutes, leaving the potential for
            response timeout.

            Upon success, a JSON response will be returned which includes a "status" of "success"
            and a "manifest_url" of the URL where the manifest file was uploaded to.
        """

        status_uri = f"https://rsp-data-exporter{self.dev_mode_url}-dot-skyviewer.uw.r.appspot.com/citizen-science-ingest-status?guid={self.guid}"
        raw_response = urllib.request.urlopen(status_uri).read()
        response = raw_response.decode('UTF-8')
        return json.loads(response)

    def download_batch_metadata(self):
        """
            This method will return the most recent manifest URL for the active project if 
            one exists.
        """

        project_id_str = str(self.project_id)
        dl_response = f"https://rsp-data-exporter{self.dev_mode_url}-dot-skyviewer.uw.r.appspot.com/active-batch-metadata?vendor_project_id={project_id_str}"
        raw_response = urllib.request.urlopen(dl_response).read()
        response = raw_response.decode('UTF-8')
        return json.loads(response)
    
    def send_tabular_data(self, subject_set_name, manifest_location):
        self.step = 0
        self.log_step("Checking batch status")
        if self.__has_active_batch() == True:
            self.log_step("Active batch exists!!! Continuing because this notebook is in debug mode")
            raise CitizenSciencePipelineError("You cannot send another batch of data while a subject set is still active on the Zooniverse platform - you can only send a new batch of data if all subject sets associated to a project have been completed.")
        
        self.log_step("Creating new subject set")
        self.__create_new_subject_set(subject_set_name)

        self.__upload_tabular_manifest(manifest_location)

        self.edc_response = self.__alert_edc_of_new_citsci_data(True) # True that the data is tabular
        
        self.process_edc_response()
        return
           
    def __upload_tabular_manifest(self, manifest_path):
        self.guid = str(uuid.uuid4())
        self.log_step("Uploading tabular data manifest")
        bucket_name = "citizen-science-data"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(self.guid + "/manifest.csv")

        blob.upload_from_filename(manifest_path)
        return

    def send_image_data(self, subject_set_name, zip_path, **options):
        """
            Sends the new data batch to the Rubin EPO Data Center for public hosting
            so that the data can be added to the target Zooniverse project.

            Several events need to have occurred for this function to complete
            successfully:
            
                1. The user must have already logged into the Zooniverse platform
                2. The user must have given their subject set a unique name and
                   passed it into the method as a named argument
                3. The user must have specified a batch directory where the manifest
                   file and the subject data exist
                4. The manifest file must be formatted correctly, see the 
                   make_manifest_with_images() function in `utils.py` in the Citizen
                   Science Notebooks repo for more details:

            https://github.com/lsst-epo/citizen-science-notebooks/blob/main/utils.py

            Upon successful completion, the manifest URL will be returned as well as a 
            message that the data was successfully process, but that more processing
            will occur on the Zooniverse platform. Once this processing is done on the 
            Zooniverse platform, the email address associated with the Zooniverse
            project should receive an email from Zoonivere stating that a new subject
            set is available.
        """

        if self.project_sanity_check() is False:
            print("Please create or specify a Zooniverse project before attempting to send image data!")
            return
        print("Send the data to Zooniverse")
        if len(subject_set_name) == 0:
            print("Please set the subject set name - did not send batch")
            return

        self.step = 0
        self.log_step("Checking batch status")
        if self.__has_active_batch() == True:
            raise CitizenSciencePipelineError("INCOMPLETE SUBJECT SET EXISTS! You cannot send another batch of data while a subject set is still active (not yet retired) on the Zooniverse platform - you can only send a new batch of data if all subject sets associated to a project have been completed.")
        self.__upload_cutouts(zip_path)
        self.__create_new_subject_set(subject_set_name)

        contains_flipbook = options.get("flipbook") if "flipbook" in options else False

        self.edc_response = self.__alert_edc_of_new_citsci_data(flipbook=contains_flipbook)
        
        self.__process_edc_response()
        return
    
    def __get_gcp_location(self):
        return base64.b64decode("L29wdC9sc3N0L3NvZnR3YXJlL2p1cHl0ZXJsYWIvc2VjcmV0cy9ydWJpbi1lcG8tY2l0LXNjaS1waXBlbGluZS5qc29u").decode("ascii")
            
    def __process_edc_response(self):
        """
            This function is called as part of the send_image_data()  workflow and should
            not be accessed publicly as unexpected results will occur.
        """

        if(self.edc_response == None):
            self.edc_response = { "status": "error", "messages": "An error occurred while processing the data transfer process upload" }
        else:                      
            self.edc_response = json.loads(self.edc_response)
        if self.edc_response["status"] == "success":
            self.manifest_url = self.edc_response["manifest_url"]
            if len(self.edc_response["messages"]) > 0:
                display("** Additional information:")
                for message in self.edc_response["messages"]:
                    logging.warning(message)
                    # display("    ** " + message)
            else:
                self.log_step("Success! The URL to the manifest file can be found here:")
                display(self.manifest_url)
        else:
            self.clean_up_unused_subject_set()
            logging.error("** One or more errors occurred during the last step **")
            logging.error(self.edc_response["messages"])
            logging.error(f"Email address: {self.email}")
            logging.error(f"Timestamp: {str(datetime.now(timezone(-timedelta(hours=7))))}")
            # for message in edc_response["messages"]:
            #     display("        ** " + message)
            return

        self.__send_zooniverse_manifest()
        self.log_step("Transfer process complete, but further processing is required on the Zooniverse platform and you will receive an email at " + self.email)
        return
    
    def zip_image_cutouts(self, batch_dir):
        """
            This function is responsible for zipping up all the cutouts that will be sent
            to the Zooniverse, and returns the path to the zip file.
        """

        if self.project_sanity_check() is False:
            print("WARNING: You haven't specified a project yet, please ensure you have specified a project before proceeding.")
        self.guid = str(uuid.uuid4())
        shutil.make_archive(f"./{self.guid}", 'zip', batch_dir)
        return [f"./{self.guid}.zip", f"{self.guid}.zip"]

    def __upload_cutouts(self, zip_path):
        """
            This function is called as part of the send_image_data()  workflow and should
            not be accessed publicly as unexpected results will occur.
        """

        self.log_step("Uploading the citizen science data")
        bucket_name = "citizen-science-data"
        destination_blob_name = zip_path[1]
        source_file_name = zip_path[0]

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)
        return

    def __alert_edc_of_new_citsci_data(self, flipbook=False, tabular = False):
        """
            This function is called as part of the send_image_data()  workflow and should
            not be accessed publicly as unexpected results will occur.
        """

        project_id_str = str(self.project_id)
        self.log_step("Notifying the Rubin EPO Data Center of the new data, which will finish processing of the data and notify Zooniverse")

        try:
            resource = "citizen-science-image-ingest" if tabular == False else "citizen-science-tabular-ingest"
            edc_endpoint = f"https://rsp-data-exporter{self.dev_mode_url}-dot-skyviewer.uw.r.appspot.com/{resource}?email={self.email}&vendor_project_id={project_id_str}&guid={self.guid}&vendor_batch_id={str(self.vendor_batch_id)}&flipbook={flipbook}&debug=True"
            # print(edc_endpoint)
            response = urllib.request.urlopen(edc_endpoint, timeout=3600).read()
            str(response)
            manifestUrl = response.decode('UTF-8')
            return manifestUrl
        except Exception as e:
            self.clean_up_unused_subject_set()
            return None
        
    def retrieve_data(self, project_id):
        """
            Given a project ID of a project that contains a completed workflow with 
            data that has been classified, this method will request the classified/
            completed data and download it if it is available.
        """

        classification_export = panoptes_client.Project(project_id).get_export(
            "classifications"
        )
        list_rows = []

        for row in classification_export.csv_reader():
            list_rows.append(row)

        return list_rows

    # def send_butler_data_to_edc():
    #     log_step("Notifying the Rubin EPO Data Center of the new data, which will finish processing of the data and notify Zooniverse")
    #     edcEndpoint = "https://rsp-data-exporter-e3g4rcii3q-uc.a.run.app/citizen-science-butler-ingest?email=" + email + "&collection=" + datasetId + "&sourceId=" + sourceId + "&vendorProjectId=" + str(projectId) + "&vendor_batch_id=" + str(vendor_batch_id)
    #     log_step('Processing data for Zooniverse, this may take up to a few minutes.')
    #     response = urllib.request.urlopen(edcEndpoint).read()
    #     manifestUrl = response.decode('UTF-8')
    #     return

    def __has_active_batch(self):
        """
            This function is called as part of the send_image_data()  workflow and should
            not be accessed publicly as unexpected results will occur.
        """

        active_batch = False
        for subject_set in self.project.links.subject_sets:
            try:
                for completeness_percent in list(subject_set.completeness.values()):
                    if completeness_percent < 1.0:
                        active_batch = True
                        break
                if active_batch:
                    break
            except:
                pass
            #     display("    ** Warning! - The Zooniverse client is throwing an error about a missing subject set, this can likely safely be ignored.");
        return active_batch

    def log_step(self, msg):
        self.step += 1
        display(str(self.step) + ". " + msg)
        return

# Custom error handling for this notebook
class CitizenSciencePipelineError(Exception):
    """
        A custom exception for describing errors that occurred due to system or human error
        while using the rubin.citsci PyPI package in the Rubin Science Platform's Notebook
        Aspect.
    """

    # Constructor or Initializer
    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return(repr(self.value))