from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
import uvicorn

app = FastAPI()

# Brevo API configuration
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'


# Pydantic model for the email data
class EmailRequest(BaseModel):
    to_email: str
    to_name: str
    subject: str
    content: str


# FastAPI route to send the email
@app.post("/send-email")
async def send_email(email_request: EmailRequest):
    # Create an instance of the TransactionalEmailsApi class
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Prepare the email data
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email_request.to_email, "name": email_request.to_name}],  # Recipient's email and name
        sender={"email": "nursinghopesneverends@gmail.com", "name": "Nurse Pro"},  # Sender's email and name
        subject=email_request.subject,  # Email subject
        html_content=email_request.content  # Email content in HTML format
    )

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
        return {"message": "Email sent successfully!"}
    except ApiException as e:
        print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")


# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
