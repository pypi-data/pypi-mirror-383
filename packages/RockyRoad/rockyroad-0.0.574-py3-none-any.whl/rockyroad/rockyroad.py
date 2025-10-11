import os


def check_for_subscription_key():
    try:
        os.environ["OCP_APIM_SUBSCRIPTION_KEY"]
        os.environ["OCP_APIM_SERVICES_SUBSCRIPTION_KEY"]
    except KeyError as e:
        print(  
            f"""ERROR: Define the environment variable {e} with your subscription key.  For example:

        export OCP_APIM_SUBSCRIPTION_KEY="INSERT_YOUR_SUBSCRIPTION_KEY"
        export OCP_APIM_SERVICES_SUBSCRIPTION_KEY="INSERT_YOUR_SUBSCRIPTION_KEY_SERVICES"

        or set ocp_apim_subscription_key during init.

        """
        )
    return


class DataServicesResource(object):
    """Interface to Data Services resources for the RockyRoad API."""
    
    def __init__(self, *args, **kw):
        base_url = str(kw["base_url"]).rstrip('/')  # Remove any trailing slashes
        services_base_url = str(kw["services_base_url"]).rstrip('/')  # Remove any trailing slashes
        serviceName = kw["serviceName"]
        version = kw["version"]
        test = kw["test"]
        ocp_apim_subscription_key = kw.get("ocp_apim_subscription_key")
        ocp_apim_services_subscription_key = kw.get("ocp_apim_services_subscription_key")
        if ocp_apim_subscription_key:
            os.environ["OCP_APIM_SUBSCRIPTION_KEY"] = ocp_apim_subscription_key
        if ocp_apim_services_subscription_key:
            os.environ["OCP_APIM_SERVICES_SUBSCRIPTION_KEY"] = ocp_apim_services_subscription_key
        check_for_subscription_key()
        
        if test:
            api_base_url = base_url + "/"
            services_api_base_url = services_base_url + "/"
        else:
            api_base_url = base_url + "/" + serviceName + "/" + version + "/"
            services_api_base_url = services_base_url + "/" + serviceName + "/" + version + "/"
        
        self._base_url = api_base_url
        self._services_base_url = services_api_base_url

    from .modules.api_info import _API_Info
    from .modules.company_specified_info import Company_Specified_Info
    from .modules.generated_forms import Generated_Forms
    from .modules.warranties import Warranties
    from .modules.inspections import Inspections
    from .modules.accounts import Accounts
    from .modules.apbs import Apbs
    from .modules.parts import Parts
    from .modules.services import Services
    from .modules.summaries import Summaries
    from .modules.machines import Machines
    from .modules.alerts import Alerts
    from .modules.docs import Docs
    from .modules.legacy import HelloWorld, Dealers as Legacy_Dealers, Customers
    from .modules.dealers import Dealers
    from .modules.companies import Companies
    from .modules.portal_users import Portal_Users
    from .modules.b2c_users import B2C_Users
    from .modules.users import Users
    from .modules.oracle_users import Oracle_Users
    from .modules.predictive_maintenance import Predictive_Maintenance
    from .modules.subscriptions import Subscriptions
    from .modules.edap import EDAP
    from .modules.engines import Engines
    from .modules.file_services import File_Services
    from .modules.information import Information
    from .modules.content_management import _Content_Management
    from .modules.calculators import _Calculators
    from .modules.oracle_knowledge_management import _Oracle_Knowledge_Management
    from .modules.oracle_installed_base_assets import _Oracle_Installed_Base_Assets
    from .modules.events import _Events
    from .modules.financials import _Financials
    from .modules.simple_forms import _Simple_Forms
    from .modules.portal_configurations import _Portal_Configurations
    from .modules.analytics import _Analytics
    from .modules.technical_content_feedback import Technical_Content_Feedback
    from .modules.business_information import Business_Information
    from .modules.machine_passcodes import Machine_Passcodes
    from .modules.documoto import Documoto

    def apiInfo(self):
        return self._API_Info(self)

    def helloWorld(self):
        return self.HelloWorld(self)

    def docs(self):
        return self.Docs(self)

    def alerts(self):
        return self.Alerts(self)

    def machines(self):
        return self.Machines(self)

    def legacyDealers(self):
        return self.Legacy_Dealers(self)

    def customers(self):
        return self.Customers(self)

    def accounts(self):
        return self.Accounts(self)

    def dealers(self):
        return self.Dealers(self)

    def companySpecifiedInfo(self):
        return self.Company_Specified_Info(self)

    def generatedForms(self):
        return self.Generated_Forms(self)

    def companies(self):
        return self.Companies(self)

    def apbs(self):
        return self.Apbs(self)

    def parts(self):
        return self.Parts(self)

    def services(self):
        return self.Services(self)

    def summaries(self):
        return self.Summaries(self)

    def warranties(self):
        return self.Warranties(self)

    def inspections(self):
        return self.Inspections(self)

    def portalUsers(self):
        return self.Portal_Users(self)

    def b2cUsers(self):
        return self.B2C_Users(self)

    def users(self):
        return self.Users(self)

    def oracleUsers(self):
        return self.Oracle_Users(self)

    def predictiveMaintenance(self):
        return self.Predictive_Maintenance(self)

    def subscriptions(self):
        return self.Subscriptions(self)

    def edap(self):
        return self.EDAP(self)

    def engines(self):
        return self.Engines(self)

    def fileServices(self):
        return self.File_Services(self)

    def information(self):
        return self.Information(self)

    def contentManagement(self):
        """Interface to Content Management resource for the RockyRoad API."""
        return self._Content_Management(self)

    def calculators(self):
        """Interface to Calculators resource for the RockyRoad API."""
        return self._Calculators(self)

    def oracleKnowledgeManagement(self):
        """Interface to Oracle Knowledge Management resource for the RockyRoad API."""
        return self._Oracle_Knowledge_Management(self)

    def oracleInstalledBaseAssets(self):
        """Interface to Oracle Installed Base Assets resource for the RockyRoad API."""
        return self._Oracle_Installed_Base_Assets(self)

    def events(self):
        """Interface to Events resource for the RockyRoad API."""
        return self._Events(self)

    def financials(self):
        """Interface to Financials resource for the RockyRoad API."""
        return self._Financials(self)

    def simpleForms(self):
        """Interface to Simple Forms resource for the RockyRoad API."""
        return self._Simple_Forms(self)

    def portalConfigurations(self):
        return self._Portal_Configurations(self)

    def analytics(self):
        return self._Analytics(self)

    def technicalContentFeedback(self):
        return self.Technical_Content_Feedback(self)

    def businessInformation(self):
        return self.Business_Information(self)

    def machinePasscodes(self):
        return self.Machine_Passcodes(self)

    def documoto(self):
        return self.Documoto(self)


class EmailServicesResource(object):
    """Interface to Email Services resources for the RockyRoad API."""

    def __init__(self, *args, **kw):
        base_url = str(kw["base_url"]).rstrip('/')  # Remove any trailing slashes
        serviceName = kw["serviceName"]
        version = kw["version"]
        test = kw["test"]
        ocp_apim_subscription_key = kw.get("ocp_apim_subscription_key")
        if ocp_apim_subscription_key:
            os.environ["OCP_APIM_SUBSCRIPTION_KEY"] = ocp_apim_subscription_key
        check_for_subscription_key()
        if test:
            api_base_url = base_url + "/"
        else:
            api_base_url = base_url + "/" + serviceName + "/" + version + "/"
        self._base_url = api_base_url

    from .modules.emails import Emails

    def emails(self):
        return self.Emails(self)


def build(
    serviceName,
    version,
    base_url,
    services_base_url=None,
    ocp_apim_subscription_key=None,
    ocp_apim_services_subscription_key=None,
    **kw
) -> DataServicesResource:
    """Returns a resource to interface with the RockyRoad API.

    Usage Examples - Data Services:

        from rockyroad.rockyroad import build

        dataservice = build(serviceName="data-services", version="v1", base_url='INSERT_URL_FOR_API')

        api_response = dataservice.helloWorld().list()

        dataservice.docs().swagger().content
        dataservice.docs().redocs().content
        dataservice.docs().openapi()

        api_response = dataservice.alerts().requests().list()
        api_response = dataservice.alerts().requests().list(creator_email='user@acme.com')
        api_response = dataservice.alerts().requests().insert(new_alert_request_json)
        api_response = dataservice.alerts().requests().delete(brand=brand, alert_request_id=alert_request_id)

        api_response = dataservice.alerts().reports().list()
        api_response = dataservice.alerts().reports().list(creator_email='user@acme.com')

        api_response = dataservice.machines().utilData().list(brand=brand, time_period='today')
        api_response = dataservice.machines().utilData().stats().list()

        api_response = dataservice.dealers().list()
        api_response = dataservice.customers().list(dealer_name=dealer_name)

        api_response = dataservice.accounts().list()
        api_response = dataservice.accounts().list(account="c123")
        api_response = dataservice.accounts().list(dealer_code="d123")
        api_response = dataservice.accounts().insert(new_account=new_account)
        api_response = dataservice.accounts().update(account=update_account)
        api_response = dataservice.accounts().delete(account="d123")

        api_response = dataservice.accounts().set_is_dealer(account="d123", is_dealer=True)
        api_response = dataservice.accounts().assign_dealer(customer_account="c123", dealer_account="d123", is_default_dealer=True, dealer_internal_account="abc")
        api_response = dataservice.accounts().assign_dealer(customer_account="c123", dealer_account="d123")
        api_response = dataservice.accounts().unassign_dealer(customer_account="c123", dealer_account="d123")

        api_response = dataservice.accounts().contacts().list(account=account)
        api_response = dataservice.accounts().contacts().list(account=account, include_dealer_contacts=True)
        api_response = dataservice.accounts().contacts().list(account_uid=account_uid)
        api_response = dataservice.accounts().contacts().list(account_contact_uid=account_contact_uid)
        api_response = dataservice.accounts().contacts().insert(new_account_contact=new_account_contact)
        api_response = dataservice.accounts().contacts().update(account_contact=account_contact)
        api_response = dataservice.accounts().contacts().delete(account_contact_uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.accounts().customers().list()
        api_response = dataservice.accounts().customers().list(dealer_account="D123")
        api_response = dataservice.accounts().customers().list(dealer_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.accounts().customers().list(dealer_branch_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.accounts().customers().list(account_association_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.accounts().customers().dealer_provided_information().list(dealer_account=dealer_account, customer_account=customer_account)
        api_response = dataservice.accounts().customers().dealer_provided_information().update(dealer_provided_information=dealer_provided_information)

        api_response = dataservice.accounts().dealers().list()
        api_response = dataservice.accounts().dealers().list(customer_account="A123")

        api_response = dataservice.companies().list()
        api_response = dataservice.companies().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.companies().list(company_name="D123")
        api_response = dataservice.companies().list(company_account="D123")
        api_response = dataservice.companies().list(company_account_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.companies().list(is_dealer=True)
        api_response = dataservice.companies().insert(company=company)
        api_response = dataservice.companies().merge(uid=uid, body={"merge_uids": [uid, uid]})
        api_response = dataservice.companies().update(uid=uid, company=company)
        api_response = dataservice.companies().delete(uid=uid)
        api_response = dataservice.companies().subscribers().list(company_uid=company_uid)
        api_response = dataservice.companies().subscribers().get(company_uid=company_uid, user_uid=user_uid)
        api_response = dataservice.companies().subscribers().insert(company_uid=company_uid, user_uid=user_uid)
        api_response = dataservice.companies().subscribers().delete(company_uid=company_uid, user_uid=user_uid)
        api_response = dataservice.companies().dealers().list(company_uid=company_uid)
        api_response = dataservice.companies().customers().list(company_uid=company_uid)
        api_response = dataservice.companies().customers().insert(company_uid=company_uid, customer_uid=user_uid, dealer_information=dealer_information)
        api_response = dataservice.companies().customers().delete(company_uid=company_uid, customer_uid=user_uid)
        api_response = dataservice.companies().customers().patch(company_uid=company_uid, customer_uid=user_uid, dealer_information=dealer_information)
        api_response = dataservice.companies().contacts().list(company_uid=company_uid, customer_uid=customer_uid)
        api_response = dataservice.companies().contacts().insert(company_uid=company_uid, customer_uid=customer_uid, contact_information=contact_information)
        api_response = dataservice.companies().contacts().update(uid=uid, contact_information=contact_information)
        api_response = dataservice.companies().contacts().delete(uid=uid)

        api_response = dataservice.companies().branches().list_for(company_uid=company_uid)
        api_response = dataservice.companies().branches().list()
        api_response = dataservice.companies().branches().list(include_machines=True)
        api_response = dataservice.companies().branches().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.companies().branches().insert(company_uid=company_uid, branch=branch)
        api_response = dataservice.companies().branches().update(uid=uid, branch=branch)
        api_response = dataservice.companies().branches().delete(uid=uid)
        api_response = dataservice.companies().branches().subscribers().list(branch_uid=branch_uid)
        api_response = dataservice.companies().branches().subscribers().insert(company_branch_subscriber=company_branch_subscriber)
        api_response = dataservice.companies().branches().subscribers().delete(company_branch_uid=uid, subscriber_uid=uid)

        api_response = dataservice.dealers().list()
        api_response = dataservice.dealers().list(dealer_code="D123")
        api_response = dataservice.dealers().list(dealer_name="D123")
        api_response = dataservice.dealers().list(dealer_account="D123")
        api_response = dataservice.dealers().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.dealers().list(dealer_account_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.dealers().insert(dealer=dealer)
        api_response = dataservice.dealers().update(dealer=dealer)
        api_response = dataservice.dealers().delete(uid=uid)
        api_response = dataservice.dealers().subscribers().list(dealer_uid=uid)
        api_response = dataservice.dealers().subscribers().insert(dealer_subscriber=dealer_subscriber)
        api_response = dataservice.dealers().subscribers().delete(dealer_uid=uid, subscriber_uid=uid)

        api_response = dataservice.dealers().branches().list()
        api_response = dataservice.dealers().branches().list(dealer_code="D123")
        api_response = dataservice.dealers().branches().list(branch_name="D123")
        api_response = dataservice.dealers().branches().list(branch_code="D123")
        api_response = dataservice.dealers().branches().list(dealer_account="D123")
        api_response = dataservice.dealers().branches().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.dealers().branches().list(dealer_account_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.dealers().branches().list(dealer_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.dealers().branches().list(include_machines=True)
        api_response = dataservice.dealers().branches().insert(dealerBranch=dealerBranch)
        api_response = dataservice.dealers().branches().update(dealerBranch=dealerBranch)
        api_response = dataservice.dealers().branches().delete(uid=uid)
        api_response = dataservice.dealers().branches().subscribers().list(dealer_branch_uid=uid)
        api_response = dataservice.dealers().branches().subscribers().list(dealer_code='d123')
        api_response = dataservice.dealers().branches().subscribers().insert(dealer_branch_subscriber=dealer_branch_subscriber)
        api_response = dataservice.dealers().branches().subscribers().delete(dealer_branch_uid=uid, subscriber_uid=uid)
        api_response = dataservice.dealers().parts().list()
        api_response = dataservice.dealers().parts().get(uid=uid)
        api_response = dataservice.dealers().parts().insert(dealer_part=dealer_part)
        api_response = dataservice.dealers().parts().update(uid=uid, dealer+part=dealer_part)
        api_response = dataservice.dealers().parts().delete(uid=uid)
        api_response = dataservice.dealers().parts().list_for_dealer(company_uid=company_uid)

        api_response = dataservice.apbs().list()
        api_response = dataservice.apbs().list(apb_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().list(brand="brand", model="model", serial="1234")
        api_response = dataservice.apbs().list(dealer_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().list(dealer_branch_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().insert(new_apb=new_apb)
        api_response = dataservice.apbs().delete(apb_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().update(apb=updated_apb)

        api_response = dataservice.apbs().status().list(apb_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().status().insert(new_apb_status=new_apb_status)
        api_response = dataservice.apbs().status().delete(apb_status_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().status().update(apb_status=updated_apb_status)

        api_response = dataservice.apbs().requests().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().requests().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().requests().insert(new_apb_request=new_apb_request)
        api_response = dataservice.apbs().requests().delete(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.apbs().requests().update(apb_request=updated_apb_request)

        api_response = dataservice.machines().catalog().list()
        api_response = dataservice.machines().catalog().list(machine_catalog_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().catalog().insert(new_machine_catalog=new_machine_catalog)
        api_response = dataservice.machines().catalog().delete(machine_catalog_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().catalog().update(machine_catalog=machine_catalog)

        api_response = dataservice.machines().list()
        api_response = dataservice.machines().list(account="a123")
        api_response = dataservice.machines().list(account_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().list(account="a123", dealer_account="d123")
        api_response = dataservice.machines().list(dealer_code="d123")
        api_response = dataservice.machines().list(owner_company_uid="07cc67f4-45d6-494b-adac-09b5cbc7e2b5", dealer_company_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().list(dealer_company_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().list(dealer_branch_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().list(branch_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().list(account_uid="123e4567-e89b-12d3-a456-426614174000", dealer_account_uid="07cc67f4-45d6-494b-adac-09b5cbc7e2b5")
        api_response = dataservice.machines().list(brand="brand", model="model", serial="1234")
        api_response = dataservice.machines().get(uid=uid)
        api_response = dataservice.machines().insert(new_machine=new_machine)
        api_response = dataservice.machines().delete(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().update(uid=uid, machine=updated_machine)
        api_response = dataservice.machines().assign_machines_to_default_dealer(customer_account="c123", ignore_machines_with_dealer=True)

        api_response = dataservice.machines().serials().list()
        api_response = dataservice.machines().models().list()
        api_response = dataservice.machines().brands().list()
        api_response = dataservice.machines().brands().list(model=model)
        api_response = dataservice.machines().product_types().list()

        api_response = dataservice.machines().telematics().list()
        api_response = dataservice.machines().telematics().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().telematics().list(machine_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().telematics().insert(telematics=telematics)
        api_response = dataservice.machines().telematics().update(telematics=telematics)
        api_response = dataservice.machines().telematics().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.machines().logs().list()
        api_response = dataservice.machines().logs().list(machine_log_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().logs().list(machine_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().logs().list(model=model, serial=serial)
        api_response = dataservice.machines().logs().insert(machine_log=machine_log)
        api_response = dataservice.machines().logs().delete(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.machines().logs().update(log=log)

        api_response = dataservice.parts().list()
        api_response = dataservice.parts().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.parts().list(partName="abc")
        api_response = dataservice.parts().list(partNumber="acme-01")
        api_response = dataservice.parts().list(isKit=True)
        api_response = dataservice.parts().list(isKitPart=True)
        api_response = dataservice.parts().list(isKit=True, isKitPart=False)
        api_response = dataservice.parts().insert(part=part)
        api_response = dataservice.parts().update(uid=uid, part=part)
        api_response = dataservice.parts().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.parts().kits().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.parts().kits().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.parts().kits().list(kitPartNumber="acme-01")
        api_response = dataservice.parts().kits().list(partNumber="acme-01")
        api_response = dataservice.parts().kits().insert(kit=kit)
        api_response = dataservice.parts().kits().update(uid=uid, kit=kit)
        api_response = dataservice.parts().kits().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.services().maintenanceIntervals().list()
        api_response = dataservice.services().maintenanceIntervals().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.services().maintenanceIntervals().list(hours=250, brand=brand, model=model, serial=serial)
        api_response = dataservice.services().maintenanceIntervals().insert(maintenanceInterval=maintenanceInterval)
        api_response = dataservice.services().maintenanceIntervals().update(maintenanceInterval=maintenanceInterval)
        api_response = dataservice.services().maintenanceIntervals().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.services().serviceReports().list()
        api_response = dataservice.services().serviceReports().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.services().serviceReports().list(model=model, serial=serial, machine_uid=machine_uid)
        api_response = dataservice.services().serviceReports().list(account_uid=account_uid, account=account)
        api_response = dataservice.services().serviceReports().insert(service_report=service_report)
        api_response = dataservice.services().serviceReports().update(service_report=service_report)
        api_response = dataservice.services().serviceReports().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.services().emails().resetServiceDueHours(email_fields=email_fields)
        api_response = dataservice.services().emails().create(email_template=email_template, email_fields=email_fields)
        api_response = dataservice.services().templates().emails().create(email_template=email_template, email_fields=email_fields)
        api_response = dataservice.services().templates().documents().create(document_template=document_template, document_fields=document_fields)
        api_response = dataservice.services().templates().pdfs().create(document_template=document_template, include_page_numbers=True, orientation="landscape", pdf_params=pdf_params)

        api_response = dataservice.summaries().machineParts().list()
        api_response = dataservice.summaries().machineParts().list(account="a123")
        api_response = dataservice.summaries().machineParts().list(dealer_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.summaries().machineParts().list(account_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.summaries().machineParts().list(account="a123", dealer_account="d123")
        api_response = dataservice.summaries().machineParts().list(account_uid="123e4567-e89b-12d3-a456-426614174000", dealer_account_uid="07cc67f4-45d6-494b-adac-09b5cbc7e2b5")
        api_response = dataservice.summaries().machineParts().list(model="model", serial="1234")

        api_response = dataservice.summaries().machineOwners().list()
        api_response = dataservice.summaries().machineOwners().list(account="a123")
        api_response = dataservice.summaries().machineOwners().list(dealer_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.summaries().machineOwners().list(account_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.summaries().machineOwners().list(account="a123", dealer_account="d123")
        api_response = dataservice.summaries().machineOwners().list(account_uid="123e4567-e89b-12d3-a456-426614174000", dealer_account_uid="07cc67f4-45d6-494b-adac-09b5cbc7e2b5")
        api_response = dataservice.summaries().machineOwners().list(model="model", serial="1234")
        api_response = dataservice.summaries().machineOwners().list(model="model", serial_range_start ="1234", engine_hours_last_twelve_months=True)

        api_response = dataservice.warranties().creditRequests().summaries().list()
        api_response = dataservice.warranties().creditRequests().summaries().list(dealer_account='d123')
        api_response = dataservice.warranties().creditRequests().summaries().list(dealer_code='d123')
        api_response = dataservice.warranties().creditRequests().summaries().list(dealer_uid='123e4567-e89b-12d3-a456-426614174000')
        api_response = dataservice.warranties().creditRequests().summaries().get(uid='123e4567-e89b-12d3-a456-426614174000')
        api_response = dataservice.warranties().creditRequests().list()
        api_response = dataservice.warranties().creditRequests().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().creditRequests().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().creditRequests().list(dealer_account="d123)
        api_response = dataservice.warranties().creditRequests().insert(creditRequest=creditRequest)
        api_response = dataservice.warranties().creditRequests().addFile(uid="123e4567-e89b-12d3-a456-426614174000", file=file)
        api_response = dataservice.warranties().creditRequests().downloadFile(uid="123e4567-e89b-12d3-a456-426614174000", filename=filename)
        api_response = dataservice.warranties().creditRequests().listFiles(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().creditRequests().update(creditRequest=creditRequest)
        api_response = dataservice.warranties().creditRequests().update(uid=uid, creditRequest=creditRequest)
        api_response = dataservice.warranties().creditRequests().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.warranties().registrations().list()
        api_response = dataservice.warranties().registrations().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().registrations().list(model=model, serial=serial, machine_uid=machine_uid)
        api_response = dataservice.warranties().registrations().list(account_uid=account_uid, account=account)
        api_response = dataservice.warranties().registrations().insert(warranty_registration=warranty_registration)
        api_response = dataservice.warranties().registrations().update(warranty_registration=warranty_registration)
        api_response = dataservice.warranties().registrations().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.warranties().creditRequests().logs().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().creditRequests().logs().list()
        api_response = dataservice.warranties().creditRequests().logs().list(warranty_credit_request_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().creditRequests().logs().insert(warranty_log=warranty_log)
        api_response = dataservice.warranties().creditRequests().logs().delete(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().creditRequests().logs().update(log=log)

        api_response = dataservice.warranties().creditRequests().snapshots().list(warranty_credit_request_uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.warranties().rates().list()
        api_response = dataservice.warranties().rates().list(include_util_data=True)
        api_response = dataservice.warranties().rates().list(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().rates().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().rates().list(dealer_branch_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().rates().list(dealer_branch_uid=uid, date=date)
        api_response = dataservice.warranties().rates().list(dealer_account="acme-01")
        api_response = dataservice.warranties().rates().list(dealer_account_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.warranties().rates().insert(warrantyRates=warrantyRates)
        api_response = dataservice.warranties().rates().update(uid=uid, warrantyRates=warrantyRates)
        api_response = dataservice.warranties().rates().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.warranties().glCodes().list()
        api_response = dataservice.warranties().glCodes().list(site=site)
        api_response = dataservice.warranties().glCodes().get(uid=uid)
        api_response = dataservice.warranties().glCodes().insert(warranty_gl_code=warranty_gl_code)
        api_response = dataservice.warranties().glCodes().update(uid=uid, warranty_gl_code=warranty_gl_code)
        api_response = dataservice.warranties().glCodes().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.warranties().productImprovements().list()
        api_response = dataservice.warranties().productImprovements().list(is_published=True)
        api_response = dataservice.warranties().productImprovements().insert(product_improvement=product_improvement)
        api_response = dataservice.warranties().productImprovements().update(uid=uid, product_improvement=product_improvement)
        api_response = dataservice.warranties().productImprovements().delete(uid="123e4567-e89b-12d3-a456-426machines614174000")

        api_response = dataservice.warranties().productImprovements().populations().insert(pip_uid=uid, population=population)
        api_response = dataservice.warranties().productImprovements().populations().update(uid=uid, population=population)
        api_response = dataservice.warranties().productImprovements().populations().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.warranties().productImprovements().machines().list()
        api_response = dataservice.warranties().productImprovements().list(machine_uid=machine_uid)
        api_response = dataservice.warranties().productImprovements().list(model=model, serial=serial)
        api_response = dataservice.warranties().productImprovements().machines().insert(pip_uid=uid, pip_machine=pip_machine)
        api_response = dataservice.warranties().productImprovements().machines().update(uid=uid, pip_machine=pip_machine)
        api_response = dataservice.warranties().productImprovements().machines().delete(uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.warranties().emails().create(emailRequest=emailRequest)
        api_response = dataservice.warranties().emails().create(useLocalTemplate=True, emailRequest=emailRequest)

        api_response = dataservice.warranties().failureModes().list()
        api_response = dataservice.warranties().failureModes().list(failure_mode_level_1="mode")

        api_response = dataservice.inspections().reports().insert(inspectionReport=inspectionReport)

        api_response = dataservice.portalUsers().list()
        api_response = dataservice.portalUsers().list(user_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.portalUsers().list(user_role='role')
        api_response = dataservice.portalUsers().list(dealer_code='d123')
        api_response = dataservice.portalUsers().list(company_uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.portalUsers().update(portal_user=portal_user)

        api_response = dataservice.b2cUsers().get(uid="123e4567-e89b-12d3-a456-426614174000")
        api_response = dataservice.b2cUsers().list()
        api_response = dataservice.b2cUsers().list(user_role='role')
        api_response = dataservice.b2cUsers().list(company_uid="123e4567-e89b-12d3-a456-426614174000")

        api_response = dataservice.subscriptions().list()
        api_response = dataservice.subscriptions().list(category_1=c1,category_2=c2,category_3=c3,category_4=c4,category_5=c5,medium='email')
        api_response = dataservice.subscriptions().categories().list()
        api_response = dataservice.subscriptions().categories().list(category_1=c1,category_2=c2,category_3=c3,category_4=c4,category_5=c5,email=True,sms=False)
        api_response = dataservice.subscriptions().categories().insert(subscription_category=subscription_category)
        api_response = dataservice.subscriptions().categories().update(uid=uid, subscription_category=subscription_category)
        api_response = dataservice.subscriptions().categories().delete(uid=uid)
        api_response = dataservice.subscriptions().users().list_subscribed_users(category_1=c1,category_2=c2,category_3=c3,category_4=c4,category_5=c5,email=True,sms=False)
        api_response = dataservice.subscriptions().users().list_subscriptions_for_user(uid=uid,category_1=c1,category_2=c2,category_3=c3,category_4=c4,category_5=c5,email=True,sms=False)
        api_response = dataservice.subscriptions().users().insert(subscription_category_uid=uid, user_uid=uid, medium='email')
        api_response = dataservice.subscriptions().users().delete(subscription_category_uid=uid, user_uid=uid, medium='email')

        api_response = dataservice.predictiveMaintenance().list()

        api_response = dataservice.edap().asset_sales().list()
        api_response = dataservice.edap().asset_sales().list(business_unit_id=bui,model=model,serial_number=serial_number)

        api_response = dataservice.information().sites().list()
        api_response = dataservice.information().brands().list()

    Usage Examples - Email Services:

        from rockyroad.rockyroad import build

        emailservice = build(serviceName="email-services", version="v1", base_url='INSERT_URL_FOR_API')

        email_message = {
            "recipient": "someone@acme.com",
            "subject": "Sending Email Message via API",
            "html_message": "This email send via the API!",
            "text_message": "This email send via the API!",
            }

        api_response = emailservice.emails().send(email_message_json)


    """
    try:
        service = {
            "data-services": DataServicesResource,
            "email-services": EmailServicesResource,
        }[serviceName]
        return service(
            serviceName=serviceName,
            version=version,
            base_url=base_url,
            services_base_url=services_base_url,
            ocp_apim_subscription_key=ocp_apim_subscription_key,
            ocp_apim_services_subscription_key=ocp_apim_services_subscription_key,
            test=kw.get("test", False),
        )
    except KeyError:
        print(
            f"ERROR:  The service name '{serviceName}' was not found or is not supported."
        )
