# healthcare-ai-call-assistant

|page_type| languages                               |products
|---|-----------------------------------------|---|
|sample| <table><tr><td>Python</tr></td></table> |<table><tr><td>azure</td><td>azure-communication-services</td></tr></table>|

# Call Automation - Quick Start Sample

This is a sample application demonstrated during Microsoft Ignite 2024. The application has been modified to work for healthcare conversations and with the outbout call automation API of Azure Communication Service. 
The app highlights an integration of Azure Communication Services with Azure OpenAI Service GPT4-Realtime and tools to enable intelligent conversational agents grounded on internal data. 

## Prerequisites

- An Azure account with an active subscription. [Create an account for free](https://azure.microsoft.com/free/?WT.mc_id=A261C142F). 
- A deployed Communication Services resource. [Create a Communication Services resource](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource).
- A [phone number](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/telephony/get-phone-number) in your Azure Communication Services resource that can get inbound calls. NB: phone numbers are not available in free subscriptions.
- [Python](https://www.python.org/downloads/) 3.7 or above.
- An Azure OpenAI Resource and Deployed Model. See [instructions](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal).


### Setup the Python environment

Create and activate python virtual environment and install required packages using following command 
```
pip install -r requirements.txt
pip install -r ./aoai-whl/rtclient-0.5.1-py3-none-any.whl
```

### Setup and host your Azure DevTunnel

[Azure DevTunnels](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/overview) is an Azure service that enables you to share local web services hosted on the internet. Use the commands below to connect your local development environment to the public internet. This creates a tunnel with a persistent endpoint URL and which allows anonymous access. We will then use this endpoint to notify your application of calling events from the ACS Call Automation service.

```bash
devtunnel create --allow-anonymous
devtunnel port create -p 8080
devtunnel host
```

### Configuring application

Open `.env` file to configure the following settings

1. `ACS_CONNECTION_STRING`: Azure Communication Service resource's connection string.
2. `CALLBACK_URI_HOST`: Base url of the app. (For local development use dev tunnel url)
3. `AZURE_OPENAI_SERVICE_ENDPOINT`: Azure Open AI service endpoint
4. `AZURE_OPENAI_SERVICE_KEY`: Azure Open AI service key
5. `AZURE_OPENAI_DEPLOYMENT_MODEL_NAME`: Azure Open AI deployment name

## Run app locally

1. Navigate to `healthcare-ai-call-assistant` folder and run `main.py` in debug mode or use command `python ./main.py` to run it from PowerShell, Command Prompt or Unix Terminal
2. Browser should pop up with the below page. If not navigate it to `http://localhost:8080/`or your dev tunnel url.
3. Register an EventGrid Webhook for the IncomingCall(`https://<devtunnelurl>/api/incomingCall`) event that points to your devtunnel URI. Instructions [here](https://learn.microsoft.com/en-us/azure/communication-services/concepts/call-automation/incoming-call-notification).

Once that's completed you should have a running application. The best way to test this is to place a call to your ACS phone number and talk to your intelligent agent.

