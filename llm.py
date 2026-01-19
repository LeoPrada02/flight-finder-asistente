import json
import openai
from config import MODEL
from flights import get_ticket_price


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_price",
            "description": "Obtiene el precio de boletos de avion en tiempo real",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin_city": {
                        "type": "string",
                        "description": "Lugar de salida"
                    },
                    "destination_city": {
                        "type": "string",
                        "description": "Ciudad de destino"
                    }
                },
                "required": ["origin_city", "destination_city"]
            }
        }
    }
]


def handle_tool_call(message):  #Una funcion que maneja la llamada a la herramienta, devuelve la respuesta de la herramienta lista para ser añadida al historial
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)

    origin_city = arguments.get("origin_city")
    destination_city = arguments.get("destination_city")

    price = get_ticket_price(origin_city, destination_city)

    response = {
        "role": "tool",
        "content": json.dumps({
            "origin_city": origin_city,
            "destination_city": destination_city,
            "price": price
        }),
        "tool_call_id": tool_call.id
    }

    return response, destination_city  #Destination city no se usa en este codigo, pero lo uso en una maquina en colab para generar imagenes


system_message = "Eres un asistente útil para una aerolínea llamada FlightAI. "
system_message += "Da respuestas breves y corteses, de no más de una oración. "
system_message += "Se siempre preciso. Si no sabes la respuesta, dilo. el usuario puede proporcionar las \
                    ciudades de partida y \
                destino en distintos idiomas, siempre traduce las ciudades a su nombre en INGLES, tienes una tool que retorna \
                un json, menciona el carrier del vuelo que encontraras en ese json"



def chat(history):  #Funcion que sera usada en el ui de gradio
    messages = [
        {"role": "system", "content": system_message}
    ] + history

    image = None

    response = openai.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    if response.choices[0].finish_reason == "tool_calls":
        
        tool_message = response.choices[0].message
        
        tool_response, destination_city = handle_tool_call(tool_message)

        messages.append(tool_message)
        messages.append(tool_response)

        #prompt = f"turistic places of {destination_city}"
        #image = pipe(prompt).images[0]

        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages
        )

    history.append({
        "role": "assistant",
        "content": response.choices[0].message.content
    })

    return history#, image

#comente las cosas que originalmente generaban imagenes, la generacion de imagenes queda disponible en el google colab