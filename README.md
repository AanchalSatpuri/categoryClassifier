# Category Classifier Lambda Function

A serverless AWS Lambda function that uses OpenAI's GPT-4o-mini model to automatically classify customer support tickets into appropriate categories based on membership type and available help categories.

## Features

- 🤖 **AI-Powered Classification**: Uses OpenAI's GPT-4o-mini for intelligent ticket categorization
- 🏢 **Membership-Aware**: Considers customer membership type when classifying tickets
- 🔄 **Service Dispatcher Pattern**: Extensible architecture for multiple service types
- ⚡ **Serverless**: Deployed on AWS Lambda for automatic scaling
- 🌐 **CORS Enabled**: Ready for web application integration
- 🔒 **Environment Variable Security**: API keys stored securely as environment variables

## Architecture

The function uses a service dispatcher pattern that routes requests based on the `type` field:

```python
service_dispatcher = {
    "HELP_AND_SUPPORT": handle_help_and_support_ticket_category,
    # Add more services here as needed
}
```

## API Usage

### Request Format

```json
{
  "type": "HELP_AND_SUPPORT",
  "data": {
    "membership_type": "Virtual Office",
    "options": [
      {"id": "67cee75cafe551182557eaa3", "label": "Account and Billing"},
      {"id": "67cee75cafe551182557eac9", "label": "Internet, A/V, and Phone"},
      {"id": "67cee75cafe551182557eac8", "label": "Other"}
    ],
    "description": "My wifi is not working properly"
  }
}
```

### Response Format

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Ticket Category Recommended Successfully",
  "data": {
    "option": [
      {
        "id": "67cee75cafe551182557eac9",
        "value": "Internet, A/V, and Phone"
      }
    ]
  }
}
```

## Deployment

### Prerequisites

1. AWS CLI configured
2. OpenAI API key
3. Python 3.9+ (for local testing)

### Environment Variables

Set the following environment variable in your Lambda function:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### AWS Lambda Deployment

1. **Create deployment package:**
   ```bash
   pip install -r requirements.txt -t .
   zip -r lambda_deployment.zip . -x "*.git*" "*.pyc" "__pycache__/*"
   ```

2. **Deploy to AWS Lambda:**
   - Create a new Lambda function
   - Upload the `lambda_deployment.zip`
   - Set the handler to `lambda_function.lambda_handler`
   - Configure environment variables
   - Set timeout to 30 seconds
   - Set memory to 256 MB (minimum)

3. **Add API Gateway Trigger:**
   - Create REST API
   - Add POST method
   - Enable CORS
   - Deploy the API

### Local Testing

```bash
# Set environment variable
export OPENAI_API_KEY="your_api_key_here"

# Test the function
python lambda_function.py
```

## Classification Logic

The function uses a multi-level classification approach:

1. **Exact Matching**: Direct string comparison
2. **Smart Partial Matching**: Keyword-based matching for complex category names
3. **Fallback**: Uses "Other" category if no match found
4. **Error Handling**: Graceful degradation with meaningful error messages

## Error Handling

The function includes comprehensive error handling:

- **400 Bad Request**: Missing required fields or invalid JSON
- **500 Internal Server Error**: OpenAI API errors or unexpected exceptions
- **Graceful Fallbacks**: Always returns a valid response even on errors

## Security

- API keys stored as environment variables
- CORS headers configured for web security
- Input validation and sanitization
- Error messages don't expose sensitive information

## Performance

- **Model Warmup**: Reduces cold start latency
- **Connection Reuse**: Optimized for Lambda execution
- **Efficient Prompting**: Minimal token usage for cost optimization
- **Fast Matching**: Multi-level classification for quick responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please create an issue in the GitHub repository. 