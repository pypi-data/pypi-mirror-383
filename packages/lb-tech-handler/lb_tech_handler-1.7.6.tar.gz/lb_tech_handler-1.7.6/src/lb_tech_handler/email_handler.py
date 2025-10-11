from ast import Not
import os
from re import I
from tkinter import NO
import requests
import base64
import mimetypes

from lb_tech_handler.sharepoint_handler import SharePointClient

from lb_tech_handler.common_methods import display_indented_text

def generate_attachment_body_local_file(
    file_path
    ):

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    # Read and encode file as base64
    with open(file_path, "rb") as f:
        content_bytes = base64.b64encode(f.read()).decode("utf-8")

    # Prepare attachment JSON
    attachment_json = {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": file_path.split("/")[-1],
        "contentType": mime_type,
        "contentBytes": content_bytes
    }

    return attachment_json
    

def generate_email_body(
        sender_email: str,
        list_of_recipients,
        subject,
        body,
        content_type: str ,
        list_of_cc_emails: list = None,
        attachments: list = None,
        is_draft: bool = False,
        save_to_sent_items: bool = True
):

    sender_email = sender_email.strip()

    to_recipients_list = []

    cc_recipients_list = []

    for each_email in list_of_recipients:
        to_recipients_list.append({
            "emailAddress": {
            "address": each_email.strip()
            }   
        })




    data_to_send = {

        "subject": subject,
        "body": {
            "contentType": content_type,
            "content": body
        },
        'from': {
            "emailAddress": {
                'address': sender_email,
                'name': "Sender",
            }
        },
        "toRecipients": to_recipients_list
    }

    if attachments is not None:
        data_to_send["attachments"] = attachments

    if list_of_cc_emails is not None:

        for each_email in list_of_cc_emails:
            cc_recipients_list.append({
                "emailAddress": {
                "address": each_email.strip()
                }   
            })

        data_to_send["ccRecipients"] = cc_recipients_list

    if not is_draft:

        final_data = {
            "message": data_to_send,
            "saveToSentItems": save_to_sent_items
        }

        return final_data

    return data_to_send



def generate_draft_email(
        sender_email: str,
        list_of_recipients,
        subject,
        body,
        headers,
        content_type: str = "Text",
        list_of_cc_emails: list = None,
        attachments: list = None,
        save_to_sent_items: bool = False
    ) -> requests.Response:

    data_to_send = generate_email_body(
        sender_email=sender_email,
        list_of_recipients=list_of_recipients,
        subject=subject,
        body=body,
        content_type=content_type,
        list_of_cc_emails=list_of_cc_emails,
        attachments=attachments,
        is_draft=True,
        save_to_sent_items=save_to_sent_items
    )
    
    response_received = requests.post(url=f"https://graph.microsoft.com/v1.0/users/{sender_email}/messages",json=data_to_send ,headers=headers)

    return response_received

if __name__ == "__main__":
    
    sender_email = "johnson@learnbasics.fun"

    list_of_recipients = ["rebeirojohnson@gmail.com"]

    subject = "Test Email"

    body = "Test Body 45"

    # attachment_list = ["Application Development - Task 1.pdf","Application Development - Task 2.pdf"]

    # attachment_list = [generate_attachment_body_local_file(file_path) for file_path in attachment_list]

    attachment_list = None

    print(attachment_list)
    
    TENANT_ID = os.getenv('TENANT_ID')
    
    CLIENT_ID = os.getenv('CLIENT_ID')
    
    CLIENT_SECRET = os.getenv('LOGIN_SECRET')
    
    SHAREPOINT_HOST_NAME = os.getenv('SHAREPOINT_HOST_NAME')

    client = SharePointClient(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        sharepoint_host_url=SHAREPOINT_HOST_NAME
    )

    client_headers = client.get_headers()

    graph_api_response = generate_draft_email(
        sender_email=sender_email,
        list_of_recipients=list_of_recipients,
        subject=subject,
        body=body,
        headers=client_headers,
        attachments=attachment_list,
    )

    display_indented_text(graph_api_response.json())



    

    
