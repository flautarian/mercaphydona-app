import base64
import io
import os
import PyPDF2

# Gmail API utils
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode

# Google API libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class Message:
    def __init__(self):
        self.subject = ""
        self.date = None
        self.objects = []
    
# utility functions
def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


def search_messages(service, subject, date_from, date_to):
    
    query = "subject: {0} before: {1} after: {2}".format(subject, date_to.strftime('%Y/%m/%d'),
                                        date_from.strftime('%Y/%m/%d'))
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages

def mark_as_read(service, query):
    messages_to_mark = search_messages(service, query)
    print(f"Matched emails: {len(messages_to_mark)}")
    return service.users().messages().batchModify(
      userId='me',
      body={
          'ids': [ msg['id'] for msg in messages_to_mark ],
          'removeLabelIds': ['UNREAD']
      }
    ).execute()

def parse_parts(service, parts, folder_name, message):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")
            if part.get("parts"):
                # recursively call this function when we see that a part
                # has parts inside
                parse_parts(service, part.get("parts"), folder_name, message)
            if mimeType == "text/plain":
                # if the email part is text plain
                if data:
                    text = urlsafe_b64decode(data).decode()
                    print(text)
            elif mimeType == "text/html":
                # if the email part is an HTML content
                # save the HTML file and optionally open it in the browser
                if not filename:
                    filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                print("Saving HTML to", filepath)
                with open(filepath, "wb") as f:
                    f.write(urlsafe_b64decode(data))
            else:
                # attachment other than a plain text or HTML
                for part_header in part_headers:
                    part_header_name = part_header.get("name")
                    part_header_value = part_header.get("value")
                    if part_header_name == "Content-Disposition":
                        if "attachment" in part_header_value:
                            # we get the attachment ID 
                            # and make another request to get the attachment itself
                            print("Saving the file:", filename, "size:", get_size_format(file_size))
                            attachment_id = body.get("attachmentId")
                            attachment = service.users().messages() \
                                        .attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                            data = attachment.get("data")
                            filepath = os.path.join(folder_name, filename)
                            if data:
                                with open(filepath, "wb") as f:
                                    f.write(urlsafe_b64decode(data))
def read_document(service, parts, message, message_object: Message):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        pdf_attachment = None
        # extract file from message in attachment
        for part in parts:
            if part['filename'] and 'pdf' in part['filename']:
                if 'attachmentId' in part['body']:
                    attachment = service.users().messages().attachments().get(userId='me', messageId=message, id=part['body']['attachmentId']).execute()
                    attachment_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    pdf_attachment = io.BytesIO(attachment_data)
                elif 'data' in part['body']:
                    attachment_data = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8'))
                    pdf_attachment = io.BytesIO(attachment_data)
                break

        # if pdf was extracted successfully we read the data with PDF2Reader and adde them to the result object
        if pdf_attachment:
            # Convert PDF to text
            pdf_reader = PyPDF2.PdfReader(pdf_attachment)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
                enable_extract_list = False
                for line in text.split("\n"):
                    if "Unit Import" in line or "TOTAL (€)" in line: # detect initial and final of the list, else we add the line as object line
                        enable_extract_list = not enable_extract_list
                    elif enable_extract_list:
                        message_object.objects.append(line)
                    
                                
                                    
def read_message(service, message):
    """
    This function takes Gmail API `service` and the given `message_id` and does the following:
        - Downloads the content of the email
        - Prints email basic information (To, From, Subject & Date) and plain/text parts
        - Downloads text/html content (if available) and reads it, extracting any ticket data into message result
    """
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    # parts can be the message body, or attachments
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    message_object = Message()
    if headers:
        # this section prints email basic info & creates a folder for the email
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == 'from':
                # we print the From address
                print("From:", value)
            if name.lower() == "to":
                # we print the To address
                print("To:", value)
            if name.lower() == "subject":
                # make our boolean True, the email has "subject"
                has_subject = True
                # make a directory with the name of the subject
                print("Subject:", value)
                message_object.subject = value
            if name.lower() == "date":
                # we print the date when the message was sent
                print("Date:", value)
                message_object.date = value
    read_document(service, parts, message, message_object)
    print("="*50)
    return message_object
    
        

def mark_as_unread(service, query):
    messages_to_mark = search_messages(service, query)
    print(f"Matched emails: {len(messages_to_mark)}")
    # add the label UNREAD to each of the search results
    return service.users().messages().batchModify(
        userId='me',
        body={
            'ids': [ msg['id'] for msg in messages_to_mark ],
            'addLabelIds': ['UNREAD']
        }
    ).execute()
    
def obtain_google_token(creds, home_folder):
    if not creds:
        """Search in the Gmail API system the mails that accomplish with the written query """
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(f"{home_folder}/token.json"):
            creds = Credentials.from_authorized_user_file(f"{home_folder}/token.json", SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as error:
                        print(f"An error occurred: {error}")
                        flow = InstalledAppFlow.from_client_secrets_file(
                        f"{home_folder}/credentials.json", SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                        
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        f"{home_folder}/credentials.json", SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(f"{home_folder}/token.json", "w") as token:
                    token.write(creds.to_json())
    return creds