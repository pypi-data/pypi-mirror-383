@Authorized
Feature: conversations endpoint API tests

  Background:
    Given The service is started locally
      And REST API service hostname is localhost
      And REST API service port is 8080
      And REST API service prefix is /v1


  Scenario: Check if conversations endpoint finds the correct conversation when it exists
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
    And I use "query" to ask question with authorization header
    """
    {"query": "Say hello"}
    """
    And The status code of the response is 200
    And I store conversation details
     When I access REST API endpoint "conversations" using HTTP GET method
     Then The status code of the response is 200
     And The conversation with conversation_id from above is returned
     And The conversation details are following
     """
     {"last_used_model": "gpt-4-turbo", "last_used_provider": "openai", "message_count": 1}
     """

  Scenario: Check if conversations endpoint fails when the auth header is not present
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
    And I use "query" to ask question with authorization header
    """
    {"query": "Say hello"}
    """
    And The status code of the response is 200
    And I store conversation details
    And I remove the auth header
     When I access REST API endpoint "conversations" using HTTP GET method
     Then The status code of the response is 400
     And The body of the response is the following
        """
        {
            "detail": "No Authorization header found"            
        }
        """

  Scenario: Check if conversations/{conversation_id} endpoint finds the correct conversation when it exists
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
    And I use "query" to ask question with authorization header
    """
    {"query": "Say hello"}
    """
    And The status code of the response is 200
    And I store conversation details
     When I use REST API conversation endpoint with conversation_id from above using HTTP GET method
     Then The status code of the response is 200
     And The returned conversation details have expected conversation_id
     And The body of the response has following messages
     """
     {"content": "Say hello", "type": "user", "content_response": "Hello", "type_response": "assistant"}
     """
     And The body of the response has the following schema
     """
     {
       "$schema": "https://json-schema.org/draft/2020-12/schema",
       "type": "object",
       "properties": {
         "conversation_id": { "type": "string" },
         "chat_history": {
           "type": "array",
           "items": {
             "type": "object",
             "properties": {
               "messages": {
                 "type": "array",
                 "items": {
                   "type": "object",
                   "properties": {
                     "content": { "type": "string" },
                     "type": { "type": "string", "enum": ["user", "assistant"] }
                   }
                 }
               },
               "started_at": { "type": "string", "format": "date-time" },
               "completed_at": { "type": "string", "format": "date-time" }
             }
           }
         }
       }
     }
     """

  Scenario: Check if conversations/{conversation_id} endpoint fails when the auth header is not present
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
    And I use "query" to ask question with authorization header
    """
    {"query": "Say hello"}
    """
    And The status code of the response is 200
    And I store conversation details
    And I remove the auth header
     When I use REST API conversation endpoint with conversation_id from above using HTTP GET method
     Then The status code of the response is 400
     And The body of the response is the following
      """
      {
          "detail": "No Authorization header found"            
      }
      """

  Scenario: Check if conversations/{conversation_id} GET endpoint fails when conversation_id is malformed
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
     When I use REST API conversation endpoint with conversation_id "abcdef" using HTTP GET method
     Then The status code of the response is 422

  Scenario: Check if conversations/{conversation_id} GET endpoint fails when llama-stack is unavailable
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
    And I use "query" to ask question with authorization header
    """
    {"query": "Say hello"}
    """
    And The status code of the response is 200
    And I store conversation details
    And The llama-stack connection is disrupted
     When I use REST API conversation endpoint with conversation_id from above using HTTP GET method
     Then The status code of the response is 503
     And The body of the response contains Unable to connect to Llama Stack

  Scenario: Check if conversations DELETE endpoint removes the correct conversation
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
    And I use "query" to ask question with authorization header
    """
    {"query": "Say hello"}
    """
    And The status code of the response is 200
    And I store conversation details
     When I use REST API conversation endpoint with conversation_id from above using HTTP DELETE method
     Then The status code of the response is 200
     And The returned conversation details have expected conversation_id
     And The body of the response, ignoring the "conversation_id" field, is the following
      """
      {"success": true, "response": "Conversation deleted successfully"}
      """
     And I use REST API conversation endpoint with conversation_id from above using HTTP GET method
     And The status code of the response is 404

  Scenario: Check if conversations/{conversation_id} DELETE endpoint fails when conversation_id is malformed
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
     When I use REST API conversation endpoint with conversation_id "abcdef" using HTTP DELETE method
     Then The status code of the response is 422

  Scenario: Check if conversations DELETE endpoint fails when the conversation does not exist
    Given The system is in default state
     When I use REST API conversation endpoint with conversation_id "12345678-abcd-0000-0123-456789abcdef" using HTTP DELETE method
     Then The status code of the response is 404

  Scenario: Check if conversations/{conversation_id} DELETE endpoint fails when llama-stack is unavailable
    Given The system is in default state
    And I set the Authorization header to Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
    And I use "query" to ask question with authorization header
    """
    {"query": "Say hello"}
    """
    And The status code of the response is 200
    And I store conversation details
    And The llama-stack connection is disrupted
     When I use REST API conversation endpoint with conversation_id from above using HTTP GET method
     Then The status code of the response is 503
     And The body of the response contains Unable to connect to Llama Stack