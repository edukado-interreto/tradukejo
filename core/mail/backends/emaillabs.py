from urllib.parse import urljoin

from anymail.backends.base_requests import AnymailRequestsBackend, RequestsPayload
from anymail.exceptions import AnymailConfigurationError
from anymail.message import AnymailRecipientStatus
from anymail.utils import (
    Attachment,
    EmailAddress,
    get_anymail_setting,
    merge_dicts_shallow,
    UNSET,
)

from mail.utils import nested_urlencode

MaybeStr = str | type[UNSET]
Emails = list[EmailAddress]

ON = "1"
API_URL = "https://api.emaillabs.net.pl/api/"


class EmailBackend(AnymailRequestsBackend):
    """
    EmailLabs API Email Backend
    """

    esp_name = "EmailLabs"
    debug_api_requests = True

    @classmethod
    def _conf(cls, name: str, default: MaybeStr = UNSET, kwargs=None) -> str:
        setting = get_anymail_setting(
            name,
            default,
            kwargs=kwargs,
            esp_name=cls.esp_name,
            allow_bare=True,
        )
        if not isinstance(setting, str):
            msg = f"Setting {name.upper()} is not a string"
            raise AnymailConfigurationError(msg) from None
        return setting

    def __init__(self, **kwargs):
        """Init options from Django settings"""
        esp_name = self.esp_name
        self.smtp_account: str = self._conf("smtp_account", kwargs=kwargs)
        self.app_key: str = self._conf("app_key", kwargs=kwargs)
        self.secret_key: str = self._conf("secret_key", kwargs=kwargs)
        api_url = urljoin(
            self._conf("api_url", default=API_URL, kwargs=kwargs), "/api/"
        )
        super().__init__(api_url, **kwargs)

    def create_session(self):
        session = super().create_session()
        session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        return session

    def build_message_payload(self, message, defaults):
        """Use Requests Basic authentication"""
        auth = (self.app_key, self.secret_key)
        return EmaillabsPayload(message, defaults, self, auth=auth)

    def raise_for_status(self, response, payload, message):
        data = response.json()
        if response.status_code == 200:
            messages = [list(item.values()).pop() for item in data["data"]]
            errors = [
                self._parse_incorrect_email(msg)
                for msg in messages
                if "incorrect" in msg
            ]
            if errors:
                some_addr_without_error = len(messages) > len(errors)
                response.status_code = 400
                reason = " And ".join([e["error"] for e in errors])
                if data["message"] == "Message sent" and some_addr_without_error:
                    reason += " Other messages might have been sent."
                response.reason = reason
                super().raise_for_status(response, payload, message)

        if response.status_code == 500:
            if reason := data.get("message"):
                response.reason = reason
        super().raise_for_status(response, payload, message)

    @classmethod
    def _parse_incorrect_email(cls, msg: str):
        # EmailLabs doesn’t accept emails in the format 'A <a@a.tld>'
        # Example message:
        # h4sh@api.emaillabs.co > Address: A <a@a.tld> is \
        # incorrect. Address has white sign.
        message_id, error_message = msg.split(" > Address: ")
        return {"message_id": message_id, "error": error_message}

    def parse_recipient_status(self, response, payload, message):
        parsed_response = self.deserialize_json_response(response, payload, message)
        status = {"success": "sent"}[parsed_response["status"]]
        if message_ids := merge_dicts_shallow(*parsed_response["data"]):
            return {
                address: AnymailRecipientStatus(message_id, status)
                for address, message_id in message_ids.items()
            }
        return {}


class EmaillabsPayload(RequestsPayload):
    def __init__(self, message, defaults, backend, *args, **kwargs):
        super().__init__(message, defaults, backend, *args, **kwargs)
        self.all_recipients = []  # used for backend.parse_recipient_status
        self.to_recipients = []  # used for backend.parse_recipient_status

    def get_api_endpoint(self):
        if "template_id" in self.data:
            return "sendmail_templates"
        return "new_sendmail"

    def init_payload(self):
        self.data = {"smtp_account": self.backend.smtp_account}

    def set_subject(self, subject):
        if subject != "":
            self.data["subject"] = subject

    def set_from_email(self, email: EmailAddress):
        self.data["from"] = email.addr_spec
        if name := email.display_name:
            self.data["from_name"] = name

    def set_recipients(self, recipient_type, emails: Emails):
        assert recipient_type in ["to", "cc", "bcc"]
        if not emails:
            return

        multi = len(emails) > 1
        if recipient_type in ["cc", "bcc"]:
            if multi:
                self.data[f"multi_{recipient_type}"] = ON
                self.data[recipient_type] = {email.addr_spec: "" for email in emails}
            else:
                self.data[recipient_type] = emails[0].addr_spec

            # used for backend.parse_recipient_status:
            self.all_recipients += emails
        if recipient_type == "to":
            self.data["to"] = {email.addr_spec: "" for email in emails}

    def set_reply_to(self, emails: Emails):
        if not emails:
            return
        if len(emails) > 1:
            self.unsupported_feature("multiple reply_to")

        self.data["reply_to"] = emails[0].addr_spec

    def set_extra_headers(self, headers=None):
        self.data["headers"].update(headers)

    def set_tags(self, tags):
        if len(tags) > 0:
            self.data["tags"] = tags

    def set_template_id(self, template_id):
        if template_id:
            self.data["template_id"] = template_id

    def set_text_body(self, body):
        self.data["text"] = body

    def set_html_body(self, body):
        # EmailLabs docs says it is not optional, but it is.
        if body:
            self.data["html"] = body

    def set_merge_data(self, merge_data):
        for email, vars in merge_data.items():
            recipent_data = self.data["to"].get(email)
            if recipent_data is None:
                continue
            if recipent_data == "":
                self.data["to"][email] = {"vars": vars}
            elif isinstance(recipent_data, dict):
                self.data["to"][email].update({"vars": vars})

    def set_merge_global_data(self, merge_global_data):
        if merge_global_data:
            self.data["global_vars"] = merge_global_data

    def add_attachment(self, attachment: Attachment):
        if attachment:
            inline = {"inline": ON} if attachment.inline else {}
            self.data.setdefault("files", {}).update(
                {
                    **{
                        "name": attachment.name or "",
                        "content": attachment.b64content,
                        "mime": attachment.mimetype,
                    },
                    **inline,
                }
            )

    def set_esp_extra(self, extra):
        self.data.update(extra)

    def serialize_data(self):
        return nested_urlencode(self.data)
