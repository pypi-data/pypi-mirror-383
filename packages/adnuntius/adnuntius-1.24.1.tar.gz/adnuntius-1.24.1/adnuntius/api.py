#!/usr/bin/env python3
"""Api client code for the Adnuntius APIs."""

__copyright__ = "Copyright (c) 2022 Adnuntius AS.  All rights reserved."

import json
import os
import requests
import time
import requests.exceptions
from adnuntius.compare_json import compare_api_json_equal
from adnuntius.util import generate_id, read_text, read_binary
from requests_toolbelt.multipart.encoder import MultipartEncoder
from collections import OrderedDict
from urllib.parse import urlparse


# technically its 1 hour, but this makes sure we don't have any
# in flight stuff executing that might fail in fun ways
AUTH_TOKEN_SAFE_EXPIRY_IN_SECS = 60 * 50


class Api:
    """
    Allows access to the Adnuntius public APIs.
    """

    def __init__(self, username, password, location, context=None, verify=False, api_key=None, masquerade_user=None,
                 headers=None, api_client=None):
        """
        Constructs the Api class. Use this to access the various API endpoints.

        :param username: API username
        :param password: API password
        :param location: URL for the api including the path, eg "https://api.adnuntius.com/api"
        :param context: the network context to use for API calls
        :param verify: verify the response from the api by comparing json packets
        """

        self.defaultAuthArgs = {}
        self.defaultArgs = {}
        if context:
            self.defaultArgs['context'] = context
        if headers is None:
            self.headers = {}
        else:
            self.headers = headers
        self.location = location
        self.username = username
        self.password = password
        self.masquerade_user = masquerade_user
        self.apiKey = api_key
        self.verify = verify
        self.authorisation = None
        self.auth_time = None
        self.refresh_token = None
        self.two_factor_code_provider = None
        self.defaultIgnore = {'url', 'objectState', 'validationWarnings', 'createUser', 'createTime', 'updateUser',
                              'updateTime'}
        if api_client is None:
            def api_client(resource, accept=None): return ApiClient(resource, self, accept=accept)
        self.api_client = api_client
        self.audit = api_client("audit")
        self.ad_units = api_client("adunits")
        self.ad_unit_tags = api_client("adunittags")
        self.advertisers = api_client("advertisers")
        self.allocation_report = api_client("allocationreport")
        self.asset = api_client("asset")
        self.available_currencies = api_client("availablecurrencies")
        self.api_keys = api_client("apikeys")
        self.simple_assets = api_client("asset")
        self.assets = api_client("assets")
        self.ax_product = api_client("axproduct")
        self.bidding = api_client('dynamicbidding')
        self.bidding_advertiser_site_stats = api_client('dynamicbidding/advertisersitestats')
        self.bidding_line_item_stats = api_client('dynamicbidding/lineitemstats')
        self.blocklists = api_client("blocklists")
        self.bulkcreatives_thirdparty = api_client("bulkcreatives/thirdparty")
        self.burn_rates = api_client("burnrates")
        self.categories = api_client("categories")
        self.categories_upload = api_client("categories/upload")
        self.cdn_assets = api_client("cdnassets")
        self.context_service_configurations = api_client("contextserviceconfigurations")
        self.coupons = api_client("coupons")
        self.creativepreview = api_client("creativepreview")
        self.creativepreviewhtml = api_client("creativepreview", accept="text/html")
        self.creatives = api_client("creatives")
        self.creative_info = api_client("creatives/info")
        self.currency_conversion = api_client("currencyconversion")
        self.custom_event_types = api_client("customeventtypes")
        self.data_export = api_client("dataexports")
        self.data_view = api_client("dataview")
        self.delivery_estimate = api_client("deliveryestimate")
        self.devices = api_client("devices")
        self.earnings_accounts = api_client("earningsaccounts")
        self.email_translations = api_client("emailtranslations")
        self.external_ad_units = api_client("externaladunits")
        self.external_demand_sources = api_client("externaldemandsources")
        self.field_mappings = api_client("fieldmappings")
        self.folders = api_client("folders")
        self.impact_report = api_client("impactreport")
        self.invoice_translations = api_client("invoicetranslations")
        self.key_values = api_client("keyvalues")
        self.key_values_upload = api_client("keyvalues/upload")
        self.keywords = api_client("keywords")
        self.layouts = api_client("layouts")
        self.layout_includes = api_client("layoutincludes")
        self.line_items = api_client("lineitems")
        self.line_item_reviews = api_client("lineitems/review")
        self.livepreview = api_client("livepreview/create")
        self.message_definitions = api_client("messagedefinitions")
        self.network_forecast = api_client("networkforecast")
        self.network_profiles = api_client("networkprofiles")
        self.network_info = api_client("networkinfo")
        self.networks = api_client("networks")
        self.notes = api_client("notes")
        self.notifications = api_client("notifications")
        self.notification_preferences = api_client("notificationpreferences")
        self.orders = api_client("orders")
        self.payment = api_client("payment")
        self.product = api_client("product")
        self.reach_estimate = api_client("reachestimate")
        self.reports = api_client("reports")
        self.report_schedules = api_client("reportschedules")
        self.report_templates = api_client("reporttemplates")
        self.roles = api_client("roles")
        self.search = api_client("search")
        self.segments = api_client("segments")
        self.segments_upload = api_client("segments/upload")
        self.segments_users_upload = api_client("segments/users/upload")
        self.signup = api_client("signup")
        self.sites = api_client("sites")
        self.rulesets = api_client("rulesets")
        self.site_groups = api_client("sitegroups")
        self.sui_layouts = api_client("sui/layout")
        self.sui_product = api_client("sui/product")
        self.sui_coupon = api_client("sui/coupon")
        self.sui_network = api_client("sui/network")
        self.stats = api_client("stats")
        self.targeting_stats = api_client("stats/targeting/impression")
        self.location_stats = api_client("stats/location/impression")
        self.targeting_templates = api_client("targetingtemplates")
        self.teams = api_client("teams")
        self.teamgroups = api_client("teamgroups")
        self.line_item_templates = api_client("lineitemtemplates")
        self.tiers = api_client("tiers")
        self.timezones = api_client("timezones")
        self.traffic = api_client("stats/traffic")
        self.triggers = api_client("triggers")
        self.user_profiles = api_client("userprofiles")
        self.user = api_client("user")
        self.users = api_client("users")
        self.workspaces = api_client("workspaces")
        self.zipped_assets = api_client("zippedassets")
        self.visitor_profile_fields = api_client("visitorprofilefields")

    def get_context(self):
        return self.defaultArgs['context']


class ApiClient:
    """
    This class provides convenience methods for a specific API endpoint.
    Typically this class would not be used directly. Instead access the endpoints via the Api class.
    """

    def __init__(self, resource_name, api_context, version="/v1", session=None, accept=None):
        """
        Construct the api endpoint client.
        :param resource_name:    name of the endpoint on the url
        :param api_context:      Api class to provide context
        :param version:         api version for the url
        :return:
        """
        self.resourceName = resource_name
        self.api = api_context
        self.version = version
        self.baseUrl = self.api.location
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session
        if accept is None:
            self.accept = "application/json"
        else:
            self.accept = accept

    def get_context(self):
        return self.api.get_context()

    def get(self, object_id, args=None, sub_resource=None):
        """
        Perform a GET request for the supplied object id.
        :param object_id:    object id used to construct the url
        :param args:         optional dictionary of query parameters
        :param sub_resource: optional sub resource
        :return:            dictionary of the JSON object returned
        """
        if args is None:
            args = {}
        headers = self.auth()
        headers['Accept-Encoding'] = 'gzip'
        headers['Accept'] = self.accept
        headers.update(self.api.headers)
        if isinstance(object_id, list):
            if len(object_id) > 1:
                sub_resource = object_id[1]
            object_id = object_id[0]
        url = self.baseUrl + self.version + "/" + self.resourceName + "/" + object_id
        if sub_resource:
            url += "/" + sub_resource
        r = self.handle_err(self.session.get(url,
                                             headers=headers,
                                             params=dict(list(self.api.defaultArgs.items()) + list(args.items()))))
        if r.text == '':
            return None
        elif self.accept == "application/json":
            return r.json()
        else:
            return r.text

    def exists(self, object_id=None, args=None):
        """
        Perform a HEAD (exists) request for the supplied object id.
        :param object_id:    object id used to construct the url
        :param args:        optional dictionary of query parameters
        :return:            dictionary of the JSON object returned
        """
        if args is None:
            args = {}
        headers = self.auth()
        headers['Accept-Encoding'] = 'gzip'
        headers['Accept'] = self.accept
        headers.update(self.api.headers)
        try:
            url = self.baseUrl + self.version + "/" + self.resourceName
            if object_id:
                url += "/" + object_id
            self.handle_err(self.session.head(
                url, headers=headers, params=dict(list(self.api.defaultArgs.items()) + list(args.items()))))
            return True
        except RuntimeError as err:
            http_err = getattr(err, "httpError", None)
            # Check for cases where this error might be indicating non-existence rather than another type of error
            if not object_id or not (http_err and http_err.response.status_code == 404):
                raise err
            # This IS a 404 error, so we now need to work out if it is from an exists method (in which case return
            # false) or something else (in which case propagate the original exception).
            # Check again without the object id and using OPTIONS
            probe = self.session.options(self.baseUrl + self.version + "/" + self.resourceName, headers=headers)
            # If it is still a 404 this means it is a different error such as the endpoint is unavailable
            if probe.status_code == 404:
                raise err
            else:
                # Endpoint exists, object does not
                return False

    def copy(self, object_id, data=None, args=None):
        return self.post(object_id=object_id, data=data, args=args, sub_resource='copy')

    def defaults(self):
        return self.query(sub_resource='defaults')

    def post(self, object_id=None, data=None, json=None, args=None, sub_resource=None):
        """
        Perform a POST request for the supplied object id.
        :param object_id:    object id used to construct the url
        :param data:         optional dictionary of form parameters
        :param json:         optional JSON object to POST
        :param args          optional dictionary of query parameters
        :param sub_resource: optional sub resource
        :return:            dictionary of the JSON object returned
        """
        if data is None and json is None:
            data = {}
        if args is None:
            args = {}
        headers = self.auth()
        headers['Accept-Encoding'] = 'gzip'
        headers['Accept'] = self.accept
        headers.update(self.api.headers)
        if json is not None:
            headers['Content-Type'] = 'application/json'
        elif isinstance(data, MultipartEncoder):
            headers['Content-Type'] = data.content_type

        url = self.baseUrl + self.version + "/" + self.resourceName
        if object_id:
            url += "/" + object_id
        if sub_resource:
            url += "/" + sub_resource

        r = self.handle_err(self.session.post(url, headers=headers, data=data, json=json,
                                              params=dict(list(self.api.defaultArgs.items()) + list(args.items()))))
        if r.text == '':
            return None
        elif self.accept == "application/json":
            return r.json()
        else:
            return r.text

    def query(self, args=None, sub_resource=None):
        """
        Perform a query (a GET from an endpoint without a specific object ID).
        :param args:        optional dictionary of query parameters
        :return:            dictionary containing a 'results' key holding a list of results
        """
        if args is None:
            args = {}
        headers = self.auth()
        headers['Accept-Encoding'] = 'gzip'
        headers['Accept'] = self.accept
        headers.update(self.api.headers)

        url = self.baseUrl + self.version + "/" + self.resourceName
        if sub_resource:
            url += "/" + sub_resource

        r = self.handle_err(self.session.get(url,
                                             headers=headers,
                                             params=dict(list(self.api.defaultArgs.items()) + list(args.items()))))
        if r.text == '':
            return None
        elif self.accept == "application/json":
            return r.json()
        else:
            return r.text

    def run(self, data, args=None, sub_resource=None):
        """
        Perform a query requiring a request body to be sent (i.e. requires POST rather than GET).
        :param data:        dictionary to be converted to json to post
        :param args:        query parameters
        :return:            dictionary containing a 'results' key holding a list of results
        """
        if args is None:
            args = {}
        headers = self.auth()
        headers['Content-Type'] = 'application/json'
        headers['Accept-Encoding'] = 'gzip'
        headers['Accept'] = self.accept
        headers.update(self.api.headers)

        params = dict(list(self.api.defaultArgs.items()) + list(args.items()))
        url = self.baseUrl + self.version + "/" + self.resourceName
        if sub_resource:
            url += "/" + sub_resource

        r = self.handle_err(self.session.post(url,
                                              headers=headers,
                                              data=json.dumps(data),
                                              params=params))
        if r.text == '':
            return None
        elif self.accept == "application/json":
            return r.json()
        else:
            return r.text

    def update(self, payload, args=None, ignore=None):
        """
        Updates the supplied object, whose payload must contain an 'id' of the object which is used to construct the url
        :param payload:     dictionary containing the object's values
        :param args:        optional dictionary of query parameters
        :param ignore:      optional set of keys to ignore when comparing the posted JSON to the response JSON.
        :return:            the JSON response from the endpoint (usually contains the entire updated object).
        """
        if 'id' not in payload:
            raise ValueError("Payload must have an id")
        if args is None:
            args = {}
        if ignore is None:
            ignore = set()

        dumps = json.dumps(payload)
        url = self.baseUrl + self.version + "/" + self.resourceName + "/" + payload['id']
        headers = self.auth()
        headers['Content-Type'] = 'application/json'
        headers['Accept-Encoding'] = 'gzip'
        headers['Accept'] = self.accept
        headers.update(self.api.headers)
        r = self.handle_err(self.session.post(url,
                                              headers=headers,
                                              data=dumps,
                                              params=dict(list(self.api.defaultArgs.items()) + list(args.items()))))
        if self.api.verify:
            assert compare_api_json_equal(payload, json.loads(r.text), set(self.api.defaultIgnore).union(ignore))
        if r.text == '':
            return None
        elif self.accept == "application/json":
            return r.json()
        else:
            return r.text

    def __do_two_factor_auth(self):
        if self.api.two_factor_code_provider:
            code = self.api.two_factor_code_provider()
        else:
            self.api.authorisation = None
            raise RuntimeError("2FA setup failure: api.two_factor_code_provider not defined")

        data = {'code': code}
        endpoint = "/authenticate/2fa"

        headers = {'Content-Type': 'application/json'}
        headers.update(self.api.headers)
        headers.update(self.api.authorisation)

        try:
            r = self.handle_err(self.session.post(self.baseUrl + endpoint, data=json.dumps(data),
                                params=self.api.defaultAuthArgs, headers=headers))
        except RuntimeError as e:
            # for a failed 2fa, we need to clear the 2FA authorisation field
            # the api will retry the entire auth process again for the next call
            self.api.authorisation = None
            raise e

        response = r.json()
        # a normal Authentication failure will already have been raised above, this catches
        # a unexpected situation where there is no access token
        if 'access_token' not in response:
            self.api.authorisation = None
            raise RuntimeError("Unexpected 2FA authentication failure in POST " + r.url)

        self.api.authorisation = {'Authorization': 'Bearer ' + response['access_token']}
        self.api.auth_time = time.time()
        self.api.refresh_token = response['refresh_token']

    def __do_password_auth(self):
        data = {'grant_type': 'password',
                'scope': 'ng_api',
                'username': self.api.username,
                'password': self.api.password}

        endpoint = "/authenticate"

        if self.api.masquerade_user:
            data.update({'masqueradeUser': self.api.masquerade_user})
            endpoint = "/masquerade"

            # its possible to pass a 2fa code as an additional argument to a masquerade auth attempt
            if self.api.two_factor_code_provider:
                code = self.api.two_factor_code_provider()
                if code:
                    data.update({'twoFactorAuthCode': code})

        headers = {'Content-Type': 'application/json'}
        headers.update(self.api.headers)

        result = self.handle_err(self.session.post(self.baseUrl + endpoint, data=json.dumps(data),
                                                   params=self.api.defaultAuthArgs, headers=headers))
        # for the special 2fa workflow
        if result.status_code == 401:
            r = result
        else:
            r = self.handle_err(result)

        response = r.json()

        # a normal Authentication failure will already have been raised above, this catches
        # an unexpected situation where there is no access token
        if 'access_token' not in response:
            self.api.authorisation = None
            raise RuntimeError("Unexpected API authentication failed in POST " + r.url)

        self.api.authorisation = {'Authorization': 'Bearer ' + response['access_token']}

        if ('scope' in response and (response['scope'] == 'TWO_FACTOR_AUTH'
                                     or response['scope'] == 'FORCED_TWO_FACTOR_AUTH')):
            self.__do_two_factor_auth()
        else:
            self.api.auth_time = time.time()
            self.api.refresh_token = response['refresh_token']

    def __do_refresh_token_auth(self):
        data = {'grant_type': 'refresh_token',
                'scope': 'ng_api',
                'refresh_token': self.api.refresh_token}

        endpoint = "/authenticate"

        headers = {'Content-Type': 'application/json'}
        headers.update(self.api.headers)

        r = self.handle_err(self.session.post(self.baseUrl + endpoint, data=json.dumps(data),
                                              params=self.api.defaultAuthArgs, headers=headers))
        try:
            response = r.json()
            if 'access_token' not in response:
                return False
            self.api.authorisation = {'Authorization': 'Bearer ' + response['access_token']}
            self.api.auth_time = time.time()
            self.api.refresh_token = response['refresh_token']
            return True
        except Exception:
            return False

    def auth(self):
        """
        Returns the authorisation header for api access. Used internally.
        """

        # if we have an existing authorisation but its approaching one hour of age, discard it and refresh.
        if self.api.authorisation and not self.api.apiKey and self.api.username and self.api.auth_time:
            current_time = time.time()

            if current_time - self.api.auth_time > AUTH_TOKEN_SAFE_EXPIRY_IN_SECS:
                if self.__do_refresh_token_auth():
                    return self.api.authorisation
                else:  # if we have a failure to refresh just drop down to re-auth, should really never happen but ...
                    self.api.authorisation = None

        if not self.api.authorisation:
            if self.api.apiKey:
                self.api.authorisation = {'Authorization': 'Bearer ' + self.api.apiKey}
            elif self.api.username:
                self.__do_password_auth()
            else:
                self.api.authorisation = {}

        return self.api.authorisation

    @staticmethod
    def handle_err(r):
        """
        Checks the status code of an HTTP response and raises an exception if it is an error. Used internally.
        """
        try:
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as httpError:
            err = RuntimeError("API Error " + str(r.request.method) + " " + str(r.url) + " response " +
                               str(r.status_code) + " " + str(r.text))
            err.httpError = httpError
            try:
                err.response = json.loads(r.text)
            except Exception:
                err.response = r.text
                pass
            raise err

    def upload_resource(self, parent, id, resource_path, content_type, args=None):
        """
        Upload a file to an API endpoint.
        :param parent:          the sub-resource name to upload to
        :param id:              the id of the object to update
        :param resource_path:   path to the file on the local filesystem
        :param content_type:    mime content type of the file
        :param args:            optional dictionary of query parameters
        :return:                dictionary of the JSON object returned
        """
        if args is None:
            args = {}
        if id is None:
            id = ''
        if parent is None:
            url = self.baseUrl + self.version + "/" + self.resourceName + "/" + id
        else:
            url = self.baseUrl + self.version + "/" + self.resourceName + "/" + parent + "/" + id

        m = MultipartEncoder({'file': (os.path.basename(resource_path), read_binary(resource_path), content_type)})

        r = self.handle_err(self.session.post(
            url,
            data=m,
            headers=dict(list(self.auth().items()) + list({'Content-Type': m.content_type}.items())),
            params=dict(list(self.api.defaultArgs.items()) + list(args.items()))))
        if r.text == '':
            return None
        else:
            return r.json()

    def upload(self, resource_path, args=None):
        """
        Upload a file to an API endpoint.
        :param resource_path:   path to the file on the local filesystem
        :param args:            optional dictionary of query parameters
        :return:                dictionary of the JSON object returned
        """
        if args is None:
            args = {}
        url = self.baseUrl + self.version + "/" + self.resourceName
        if resource_path is list:
            files = {}
            for rp in resource_path:
                files['x'] = read_text(rp)
        else:
            files = {'file': read_text(resource_path)}
        r = self.handle_err(self.session.post(
            url,
            files=files,
            headers=self.auth(),
            params=dict(list(self.api.defaultArgs.items()) + list(args.items()))))
        if r.text == '':
            return None
        else:
            return r.json()


class AdServer:
    """
    Provides access to the Adnuntius Ad Delivery Server.
    """
    def __init__(self, base_url="https://delivery.adnuntius.com", session=None, resolve_to_ip=None, port=None):
        """
        Construct the class.
        :param base_url: schema and host of the Ad Delivery server. Defaults to "http://delivery.adnuntius.com"
        :param session: Defaults to a python requests session. For testing you can pass in another session type.
        :param resolve_to_ip: Send all requests to the specified IP, if it is one of the IPs that base_url resolves to.
        :param port: Defaults to 80 for http or 443 for https. If you are testing a local AdServer set its port here.
        """
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session
        if resolve_to_ip is not None and base_url.startswith("https"):
            raise ValueError("resolve to IP not currently supported with https")
        self.resolve_to_ip = resolve_to_ip
        if urlparse(base_url).port is None:
            self.base_url = base_url
            if port is None:
                if self.base_url.startswith("https"):
                    self.port = 443
                else:
                    self.port = 80
            else:
                if isinstance(port, int):
                    self.port = port
                else:
                    raise ValueError("port must be an integer")
        else:
            self.base_url = urlparse(base_url).scheme + "://" + urlparse(base_url).hostname
            self.port = urlparse(base_url).port

    def __get_base_url(self, headers):
        """
        Modifies the base url to account for any resolve_to_ip and overridden ports
        """
        if self.resolve_to_ip is None:
            return self.base_url + ':' + str(self.port)
        else:
            headers['host'] = urlparse(self.base_url).hostname
            return "http://" + self.resolve_to_ip + ':' + str(self.port)

    """
    Makes a request for creative / placement tag.
    :param tag_params:    tag params
    :param cookies:       optional dictionary of cookies
    :param headers:       optional dictionary of headers
    :return:              the python requests response object. Response content can be accessed using response.text
    """
    def request_tag(self, tag_params=None, cookies=None, headers=None):
        if not cookies:
            cookies = {}
        if not headers:
            headers = {}
        if not tag_params:
            tag_params = {}
        headers['Accept-Encoding'] = 'gzip'
        parameters = OrderedDict()
        parameters.update(tag_params)
        r = self.session.get(self.__get_base_url(headers) + "/i", params=parameters, cookies=cookies, headers=headers)
        return r

    def request_ad_unit(self, ad_unit, cookies=None, headers=None, extra_params=None):
        """
        Makes a request for an ad unit.
        :param ad_unit:       the id of the ad unit.
        :param cookies:       optional dictionary of cookies
        :param headers:       optional dictionary of headers
        :param extra_params:  optional dictionary of query parameters
        :return:              the python requests response object. Response content can be accessed using response.text
        """
        if not cookies:
            cookies = {}
        if not headers:
            headers = {}
        if not extra_params:
            extra_params = {}
        headers['Accept-Encoding'] = 'gzip'
        parameters = OrderedDict({'auId': ad_unit})
        parameters.update(extra_params)
        r = self.session.get(self.__get_base_url(headers) + "/i", params=parameters, cookies=cookies, headers=headers)
        return r

    def request_ad_units(self, ad_units, cookies=None, headers=None,
                         extra_params=None, meta_data=None, key_values=None, query_params=None):
        """
        Makes a request for multiple ad units using a composed ad tag.
        :param ad_units: list of ids of the ad unit OR list of ad-unit request objects.
        :param cookies:  optional dictionary of cookies
        :param headers:  optional dictionary of headers
        :param extra_params:  optional dictionary of parameters to include in composed request
        :return:         the python requests response object. Response content can be accessed using response.text
        """
        if not isinstance(ad_units, list):  # An accidental string here will create an ad unit for every character.
            raise ValueError("Specified Ad Units must be list")
        if not cookies:
            cookies = {}
        if not meta_data:
            meta_data = {}
        final_headers = {'Content-type': 'application/json', 'Accept-Encoding': 'gzip'}
        if headers:
            final_headers.update(headers)
        data = {'adUnits': [], 'metaData': meta_data}

        for ad_unit in ad_units:
            if isinstance(ad_unit, str):
                # Create an ad-unit request from the supplied auId
                ad_unit = {'auId': ad_unit, 'targetId': generate_id()}
                if key_values:
                    ad_unit['kv'] = key_values
            data['adUnits'].append(ad_unit)

        if extra_params:
            data.update(extra_params)

        if query_params:
            params = query_params
        else:
            params = {'tt': 'composed'}

        r = self.session.post(self.__get_base_url(headers) + "/i", data=json.dumps(data), params=params,
                              cookies=cookies, headers=final_headers)
        return r

    def request_rtb_ad_unit(self, ad_unit, request=None, cookies=None, headers=None):
        """
        Makes a request for an ad unit.
        :param ad_unit:       the ad unit.
        :param request:       optional RTB request. Will be filled with default values if only ad_unit is supplied
        :param cookies:       optional dictionary of cookies
        :param headers:       optional dictionary of headers
        :return:              the python requests response object. Response content can be accessed using response.text
        """
        if not cookies:
            cookies = {}
        if not headers:
            headers = {}
        headers['Accept-Encoding'] = 'gzip'

        impression = {
            "id": 1,
            "instl": 0,
            "tagid": ad_unit['tagId'],
            "bidfloor": 0.0,
            "bidfloorcur": "USD",
            "banner": {
                "w": ad_unit['width'],
                "h": ad_unit['height']
            }
        }

        site = {
            "id": 0,
            "name": "",
            "domain": "",
            "publisher": {
                "id": 0,
                "name": "",
                "domain": ""
            }
        }

        device = {
            "ua": "",
            "ip": "127.0.0.1"
        }

        user = {
            "id": generate_id(),
            "buyeruid": generate_id()
        }

        data = {
            "id": generate_id(),
            "at": 2,
            "bcat": [],
            "badv": [],
            "imp": [impression],
            "site": site,
            "device": device,
            "user": user
        }

        # Override the defaults if something is supplied
        if request is not None:
            data.update(request)

        r = self.session.post(self.__get_base_url(headers) + "/rtb",
                              data=json.dumps(data), cookies=cookies, headers=headers)
        return r

    def request_viewable_ad_unit(self, ad_unit, response_token, cookies=None, headers=None):
        """
        Makes a viewable impression request for an ad unit. This requires the ad unit to have previously been requested.
        :param ad_unit:        the id of the ad unit.
        :param response_token: the ad server token provided in the rt field of the original requests response object.
        :param cookies:        optional dictionary of cookies
        :param headers:        optional dictionary of headers
        :return:               the python requests response object. Response content can be accessed using response.text
        """
        if not cookies:
            cookies = {}
        if not headers:
            headers = {}
        parameters = {'auId': ad_unit}
        parameters.update({'rt': response_token})
        r = self.session.get(self.__get_base_url(headers) + "/v", params=parameters, cookies=cookies, headers=headers)
        return r

    def set_retarget_key_values(self, network_id, key_values, expiry):
        """
        Sets some re-targeting key-values on the user's cookie
        :param network_id:     the network id
        :param key_values:     a map of the key-values
        :return:               the python requests response object. Response content can be accessed using response.text
        """
        data = {
            'network': network_id,
            'keyValues': []
        }
        for key in key_values:
            data['keyValues'].append(
                {
                    'key': key,
                    'value': key_values[key],
                    'expiry': expiry
                }
            )
        headers = {}
        r = self.session.post(self.__get_base_url(headers) + "/r", data=json.dumps(data), headers=headers)
        return r

    def trigger_conversion(self, conversion_event=None, network_id=None, source_id=None, headers=None, meta_data=None):
        """
        Triggers a conversion event
        :return:               the python requests response object. Response content can be accessed using response.text
        """
        if not headers:
            headers = {}

        data = {
            'network': network_id,
            'adSource': source_id,
            'eventType': conversion_event,
            'metaData': meta_data
        }
        r = self.session.post(self.__get_base_url(headers) + "/pixelc.gif", data=json.dumps(data), headers=headers)
        return r

    def trigger_event(self, url, headers=None):
        """
        Triggers an event by requesting a URL. Uses the ad-server session so that cookies are shared.
        :param url: the url to request
        :param headers: any additional headers to add to the request
        :return:
        """
        if url[0:2] == '//':
            url = "http:" + url
        r = self.session.get(url, allow_redirects=False, headers=headers)
        return r

    def post_event(self, url, event):
        """
        Triggers a event by POST data
        :return: the python requests response object. Response content can be accessed using response.text
        """
        if url[0:2] == '//':
            url = "http:" + url
        r = self.session.post(url, allow_redirects=False, data=json.dumps(event))
        return r

    def clear_cookies(self):
        """
        Clears cookies from this session
        :return:
        """
        self.session.cookies.clear()

    def set_consent(self, network_id, consent=None, no_cookies=False):
        """
        Sets consents on the user's cookie
        :param network_id:     the network id
        :param consent:        a list of consents
        :param no_cookies:     block tracking cookies
        :return:               the python requests response object. Response content can be accessed using response.text
        """
        if consent is None:
            consent = []
        data = {
            'network': network_id,
            'consent': [],
            'blockTrackingCookies': no_cookies
        }
        if isinstance(consent, str):
            data['consent'].append(consent)
        else:
            for c in consent:
                data['consent'].append(c)
        headers = {}
        return self.session.post(self.__get_base_url(headers) + "/consent", data=json.dumps(data), headers=headers)

    def get_consent(self, network_id):
        """
        Gets the consent set on a user's cookie.
        :param network_id:     the network id
        :return:               the python requests response object. Response content can be accessed using response.text
        """
        headers = {}
        return self.session.get(self.__get_base_url(headers) + "/consent?network=" + network_id, headers=headers)


class DataServer:
    """
    Provides access to the Adnuntius data server.
    """
    def __init__(self, base_url="https://data.adnuntius.com", session=None, resolve_to_ip=None, port=None):
        """
        :param base_url: schema and host of the data server host. Defaults to "https://data.adnuntius.com"
        :param session: Defaults to a python requests session. For testing you can pass in another session type.
        :param resolve_to_ip: Send all requests to the specified IP, if it is one of the IPs that base_url resolves to.
        :param port: Defaults to 80 for http or 443 for https. If you are testing a local AdServer set its port here.
        """
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session
        if resolve_to_ip is not None and base_url.startswith("https"):
            raise ValueError("resolve to IP not currently supported with https")
        self.resolve_to_ip = resolve_to_ip
        if urlparse(base_url).port is None:
            self.base_url = base_url
            if port is None:
                if self.base_url.startswith("https"):
                    self.port = 443
                else:
                    self.port = 80
            else:
                if isinstance(port, int):
                    self.port = port
                else:
                    raise ValueError("port must be an integer")
        else:
            self.base_url = urlparse(base_url).scheme + "://" + urlparse(base_url).hostname
            self.port = urlparse(base_url).port

    def __get_base_url(self, headers):
        """
        Modifies the base url to account for any resolve_to_ip and overridden ports
        """
        if self.resolve_to_ip is None:
            return self.base_url + ':' + str(self.port)
        else:
            headers['host'] = urlparse(self.base_url).hostname
            return "http://" + self.resolve_to_ip + ':' + str(self.port)

    def visitor(self, folder=None, browser=None, profile_values=None, network=None, user_id=None, cookies=None,
                headers=None, extra_params=None):
        """
        Makes a visitor request.
        :param folder:        the id of the folder
        :param browser:       the id of the browser (i.e. user)
        :param network:       the id of the network
        :param user_id:        the id of the user in an external system
        :param profile_values: dictionary of values to update in the user profile
        :param cookies:       optional dictionary of cookies
        :param headers:       optional dictionary of headers
        :param extra_params:  optional dictionary of query parameters
        :return:              the python requests response object. Response content can be accessed using response.text
        """
        if not cookies:
            cookies = {}
        if not headers:
            headers = {}
        if not extra_params:
            extra_params = {}
        headers['Accept-Encoding'] = 'gzip'
        data = {
            'profileValues': profile_values
        }
        if folder is not None:
            data['folderId'] = folder
        if browser is not None:
            data['browserId'] = browser
        if network is not None:
            data['networkId'] = network
        if user_id is not None:
            data['externalSystemUserId'] = user_id

        r = self.session.post(self.__get_base_url(headers) + "/visitor", data=json.dumps(data), params=extra_params,
                              cookies=cookies, headers=headers)
        return r

    def page(self, domain, folder=None, browser=None, network=None, keywords=None, categories=None, cookies=None,
             headers=None, extra_params=None):
        """
        Makes a page-view request.
        :param domain:        the domain name
        :param folder:        the id of the folder
        :param browser:       the id of the browser (i.e. user)
        :param network:       the id of the network
        :param keywords:      list of keywords
        :param categories:    list of categories
        :param cookies:       optional dictionary of cookies
        :param headers:       optional dictionary of headers
        :param extra_params:  optional dictionary of query parameters
        :return:              the python requests response object. Response content can be accessed using response.text
        """
        if not cookies:
            cookies = {}
        if not headers:
            headers = {}
        if not extra_params:
            extra_params = {}
        if not keywords:
            keywords = []
        if not categories:
            categories = []

        headers['Accept-Encoding'] = 'gzip'
        headers['Referer'] = domain
        data = {
            'keywords': keywords,
            'categories': categories,
        }
        if folder is not None:
            data['folderId'] = folder
        if browser is not None:
            data['browserId'] = browser
        if network is not None:
            data['networkId'] = network

        r = self.session.post(self.__get_base_url(headers) + "/page", data=json.dumps(data), params=extra_params,
                              cookies=cookies, headers=headers)
        return r

    def sync(self, folder=None, browser=None, user_id=None, cookies=None, headers=None, extra_params=None):
        """
        Makes a sync request.
        :param folder:        the id of the folder
        :param browser:       the id of the browser (i.e. user)
        :param user_id:        the id of the user in an external system
        :param cookies:       optional dictionary of cookies
        :param headers:       optional dictionary of headers
        :param extra_params:  optional dictionary of query parameters
        :return:              the python requests response object. Response content can be accessed using response.text
        """
        if not cookies:
            cookies = {}
        if not headers:
            headers = {}
        if not extra_params:
            extra_params = {}
        headers['Accept-Encoding'] = 'gzip'
        data = dict()
        if folder is not None:
            data['folderId'] = folder
        if browser is not None:
            data['browserId'] = browser
        if user_id is not None:
            data['externalSystemUserId'] = user_id

        r = self.session.post(self.__get_base_url(headers) + "/sync", data=json.dumps(data), params=extra_params,
                              cookies=cookies, headers=headers)
        return r

    def consent(self, params=None):
        """
        Makes a consent request.
        :param params:  optional dictionary of query parameters
        :return:              the python requests response object. Response content can be accessed using response.text
        """
        if not params:
            params = {}
        headers = {}
        r = self.session.get(self.__get_base_url(headers) + "/consent", params=params, headers=headers)
        return r

    def universal_user_id(self, browser=None, folder=None, params=None):
        """
        Fetches the universal user id (if available) for a user.
        :param folder:
        :param browser:
        :param params:  optional dictionary of query parameters
        :return:              the python requests response object. Response content can be accessed using response.text
        """
        if not params:
            params = {}
        if browser:
            params['browserId'] = browser
        if folder:
            params['folderId'] = folder
        headers = {}
        r = self.session.get(self.__get_base_url(headers) + "/uui", params=params, headers=headers)
        return r

    def clear_cookies(self):
        """
        Clears cookies from this session
        :return:
        """
        self.session.cookies.clear()
