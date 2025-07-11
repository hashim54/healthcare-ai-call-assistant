import asyncio
import json
import os
from  rtclient import (
    RTLowLevelClient,
    SessionUpdateMessage,
    ServerVAD, 
    SessionUpdateParams, 
    InputAudioBufferAppendMessage, 
    InputAudioTranscription,
    )
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential,get_bearer_token_provider

active_websocket = None
answer_prompt_system_template = """ 
First thing let the user know this call will be recorded. " \
"You are a health care AI assistant that confirms provider information from users. You will start the conversation by communicating to the user that your sole purpose is to confirm the provider information. " \
"You will not answer any other questions or provide any other information. " \
"You will only ask if the below information is correct. One field at a time. For example; is the 'ProviderName' xyz? " \
"If the user tries to discuss anything other than confirming the below information, you will say 'I cannot answer that' and you will redirect them back " \
"to confirming information. " \
"Please confirm the following information:" \
"{  
"ProviderID": 1,  
"ProviderName": "XYZ Provder",  
"FirstName": "Chandler",  
"LastName": "Dixon",  
"ProviderPhoneNumber": "19108855808",  
"RenderingID": 646464565,  
"ProvTAXID": 54646  
}
"""
AZURE_OPENAI_SERVICE_ENDPOINT = os.environ["AZURE_OPENAI_SERVICE_ENDPOINT"]
AZURE_OPENAI_SERVICE_KEY = os.environ["AZURE_OPENAI_SERVICE_KEY"]
AZURE_OPENAI_DEPLOYMENT_MODEL_NAME = os.environ["AZURE_OPENAI_DEPLOYMENT_MODEL_NAME"]

async def start_conversation():
    global client
    # client = RTLowLevelClient(url=AZURE_OPENAI_SERVICE_ENDPOINT, key_credential=AzureKeyCredential(AZURE_OPENAI_SERVICE_KEY), azure_deployment=AZURE_OPENAI_DEPLOYMENT_MODEL_NAME)
    client = RTLowLevelClient(url=AZURE_OPENAI_SERVICE_ENDPOINT, key_credential=AzureKeyCredential(AZURE_OPENAI_SERVICE_KEY), azure_deployment=AZURE_OPENAI_DEPLOYMENT_MODEL_NAME)

    await client.connect()
    await client.send(
            SessionUpdateMessage(
                session=SessionUpdateParams(
                    instructions=answer_prompt_system_template,
                    turn_detection=ServerVAD(type="server_vad"),
                    voice= 'shimmer',
                    input_audio_format='pcm16',
                    output_audio_format='pcm16',
                    input_audio_transcription=InputAudioTranscription(model="whisper-1")
                )
            )
        )
    
    asyncio.create_task(receive_messages(client))
    
async def send_audio_to_external_ai(audioData: str):
    await client.send(message=InputAudioBufferAppendMessage(type="input_audio_buffer.append", audio=audioData, _is_azure=True))

async def receive_messages(client: RTLowLevelClient):
    while not client.closed:
        message = await client.recv()
        if message is None:
            continue
        match message.type:
            case "session.created":
                print("Session Created Message")
                print(f"  Session Id: {message.session.id}")
                pass
            case "error":
                print(f"  Error: {message.error}")
                pass
            case "input_audio_buffer.cleared":
                print("Input Audio Buffer Cleared Message")
                pass
            case "input_audio_buffer.speech_started":
                print(f"Voice activity detection started at {message.audio_start_ms} [ms]")
                await stop_audio()
                pass
            case "input_audio_buffer.speech_stopped":
                pass
            case "conversation.item.input_audio_transcription.completed":
                print(f" User:-- {message.transcript}")
            case "conversation.item.input_audio_transcription.failed":
                print(f"  Error: {message.error}")
            case "response.done":
                print("Response Done Message")
                print(f"  Response Id: {message.response.id}")
                if message.response.status_details:
                    print(f"  Status Details: {message.response.status_details.model_dump_json()}")
            case "response.audio_transcript.done":
                print(f" AI:-- {message.transcript}")
            case "response.audio.delta":
                await receive_audio_for_outbound(message.delta)
                pass
            case _:
                pass
                
async def init_websocket(socket):
    global active_websocket
    active_websocket = socket

async def receive_audio_for_outbound(data):
    try:
        data = {
            "Kind": "AudioData",
            "AudioData": {
                    "Data":  data
            },
            "StopAudio": None
        }

        # Serialize the server streaming data
        serialized_data = json.dumps(data)
        await send_message(serialized_data)
        
    except Exception as e:
        print(e)

async def stop_audio():
        stop_audio_data = {
            "Kind": "StopAudio",
            "AudioData": None,
            "StopAudio": {}
        }

        json_data = json.dumps(stop_audio_data)
        await send_message(json_data)

async def send_message(message: str):
    global active_websocket
    try:
        await active_websocket.send(message)
    except Exception as e:
        print(f"Failed to send message: {e}")

