import json
from abc import ABC, abstractmethod
from typing import Type
from requests.models import Response


class ResponseInterface:
    """
    Abstract base class for LLM response.
    Defines methods to parse messages.
    """
    @abstractmethod
    def parse_stream_response(self, chunk, **kwargs):
        """Parse the stream response from the LLM."""
        pass

    @abstractmethod
    def parse_full_response(self, payload):
        """Parse the full response from the LLM."""
        pass

    @abstractmethod
    def _generate_event(self, buffer):
        """Generate SSE event from the given data."""
        pass

#Default
class ChatResponse(ResponseInterface):
    def __init__(self, end_token = "<|eot_id|>"):
        #SSE type of response
        self.eot_token = end_token

    def parse_stream_response(self, chunk: bytes, sse = False):
        if not chunk:
            v = ""

        chunk_str = chunk.decode('utf-8').strip()
        if not chunk_str or not chunk_str.startswith("data:"):
            v = ""

        data_str = chunk_str[len("data:"):].strip()
        if data_str == "[DONE]":
            v = "[DONE]"

        try:
            chunk_data = json.loads(data_str)
            delta_content = chunk_data['choices'][0]['delta'].get('content', '')
            v = "" if delta_content == self.eot_token else delta_content

        except json.JSONDecodeError:
            v = ""


        if sse:
            return self._generate_event(v)
        else:
            return v
            
    def _generate_event(self, buffer):
        event = {}
        event["v"] = "".join(buffer)
        return f"event: delta\ndata: {json.dumps(event)}\n\n"

    def parse_full_response(self, payload):
        #TODO try to parse vllm whole response
        return payload


class StreamResponseBuffer:
    def __init__(self, llm_response: Type[ResponseInterface], headers=None, eot_token = "<EOT_TOKEN>"):
        self.headers= headers
        self.llm_response = llm_response
        self.eot_token = eot_token

    async def stream(self, response: Response, buffer_size=10, trigger_connection = None):
        # Buffer to accumulate chunks until they form a complete sentence or exceed batch_size
        buffer = []

        if response.status_code == 200:
            # Iterate over the response stream
            for chunk in response.iter_lines():
                if trigger_connection:
                    if await trigger_connection.is_disconnected():
                        response.close()
                        break
                
                delta_content = self.llm_response.parse_stream_response(chunk)
                
                if delta_content == self.eot_token:
                    break  

                if buffer_size > 0:
                    buffer.append(delta_content)

                # Check if the buffer has reached the max length
                if self._is_buffer_full(buffer, buffer_size):
                    # Join the buffer into a complete chunk and yield as event
                    print( self.llm_response._generate_event(buffer))
                    
                    # Reset the buffer
                    buffer.clear()

            # Yield the final event if there's any remaining content in the buffer
            if buffer:
                yield self.llm_response._generate_event(buffer)

        else:
            print(f"Error: {response.status_code}, {response.text}")


    # based on character length 
    # def _is_buffer_full(self, buffer, buffer_size):
    #     """Check if the buffer has reached the specified max length."""
    #     return sum(len(word) for word in buffer) + len(buffer) - 1 >= buffer_size
    
    def _is_buffer_full(self, buffer, buffer_size):
        """Check if the buffer has reached the specified max length."""
        #TODO: right now it is based on the number of chunks, it could be based on other advanced metrics
        return  len(buffer) >= buffer_size
