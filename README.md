# AI Persona Image Generator

An automated Python application that generates unique, realistic images for organizational administrators using OpenAI for prompt generation and Stable Diffusion for image creation.

## Features

- **Hierarchical JSON Data Processing**: Reads administrator data from organized JSON files in categories and subcategories
- **Database Storage**: SQLite database for data persistence and tracking with category support
- **AI Prompt Generation**: Uses OpenAI GPT-4o to create detailed Stable Diffusion prompts
- **Image Generation**: Generates high-quality images using local Stable Diffusion (Automatic1111)
- **Modular Workflow**: Step-by-step processing with individual control options
- **Progress Tracking**: Database flags track prompt and image generation status
- **Category Management**: Organize data by categories and subcategories for better organization

## Prerequisites

### 1. Local Stable Diffusion Setup

Ensure you have Automatic1111 Web UI installed and running:

```bash
# Start Automatic1111 with API enabled
./webui-user.sh --api
```

**Important**: The Web UI must be running on `http://127.0.0.1:7860` with the `--api` flag.

### 2. Recommended Models

For best results, load a high-quality photorealistic model in Automatic1111:
- RealVisXL
- Absolute Reality
- Epicrealism
- Photon

### 3. Python Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

Before running the application, update the configuration in `config.py`:

```python
# Replace with your actual OpenAI API key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Replace with your actual model filename (e.g., "realvisxl_v4.safetensors")
SD_MODEL_CHECKPOINT = "your_model_name.safetensors"
```

## Data Organization

The application now supports hierarchical data organization. Place your JSON files in the `data/` directory with the following structure:

```
data/
├── universities/              # Category: Universities
│   ├── medical_schools.json   # Subcategory: Medical Schools
│   ├── engineering.json       # Subcategory: Engineering
│   └── business_schools.json  # Subcategory: Business Schools
├── hospitals/                 # Category: Hospitals
│   ├── general.json           # Subcategory: General Hospitals
│   ├── specialized.json       # Subcategory: Specialized Hospitals
│   └── research.json          # Subcategory: Research Hospitals
└── research_institutes/       # Category: Research Institutes
    ├── technology.json        # Subcategory: Technology
    └── medicine.json          # Subcategory: Medicine
```

### Input Data Format

Each JSON file should contain a list of administrator objects with the following structure:

```json
[
  {
    "prv": {
      "org": {
        "admin": {
          "id": 123,
          "fname": "John",
          "sname": "Doe",
          "contacts": {
            "email": "john.doe@example.com",
            "phoneNumber": "+1234567890"
          }
        },
        "name": "Example Organization",
        "contacts": {
          "address": {
            "town": "Example City"
          }
        },
        "langs": ["English", "Spanish"]
      }
    }
  }
]
```

## Usage

### Command Line Options

The application provides several command-line options for flexible workflow control:

```bash
# Parse JSON data into database
python main.py --parse-json

# Generate prompts for profiles without prompts
python main.py --generate-prompts

# Generate images for profiles with prompts but no images
python main.py --generate-images

# Run complete pipeline (all steps)
python main.py --all

# Validate configuration
python main.py --validate

# Show help
python main.py --help
```

### Database Utilities

Use `db_utils.py` for database inspection and management:

```bash
# View all profiles
python db_utils.py --view-all

# View profiles by category
python db_utils.py --view-category universities

# View profiles by category and subcategory
python db_utils.py --view-subcategory universities medical_schools

# View all categories and subcategories
python db_utils.py --view-categories

# View generation status
python db_utils.py --view-status

# View generated prompts
python db_utils.py --view-prompts

# View specific profile details
python db_utils.py --view-profile 1
```

### Recommended Workflow

1. **Setup**: Ensure Automatic1111 is running with API enabled
2. **Organize Data**: Place JSON files in appropriate category/subcategory folders
3. **Parse Data**: `python main.py --parse-json`
4. **Review**: Check the database to ensure data was parsed correctly
5. **Generate Prompts**: `python main.py --generate-prompts`
6. **Review Prompts**: Check generated prompts in the database
7. **Generate Images**: `python main.py --generate-images`

## Database Schema

The application creates a SQLite database (`profiles.db`) with the following table:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| json_source_file | TEXT | Source JSON file path |
| category | TEXT | Category (e.g., universities, hospitals) |
| subcategory | TEXT | Subcategory (e.g., medical_schools, general) |
| admin_id | INTEGER | Unique admin identifier |
| first_name | TEXT | Administrator's first name |
| last_name | TEXT | Administrator's last name |
| email | TEXT | Email address |
| phone_number | TEXT | Phone number |
| organization_name | TEXT | Organization name |
| organization_town | TEXT | Organization location |
| languages | TEXT | Comma-separated languages |
| positive_prompt | TEXT | Generated positive prompt |
| negative_prompt | TEXT | Generated negative prompt |
| image_path | TEXT | Generated image filename |
| prompt_generated | INTEGER | Flag (0/1) |
| image_generated | INTEGER | Flag (0/1) |
| created_at | TIMESTAMP | Record creation timestamp |

## Output

Generated images are saved in the `generated_images/` directory with filenames in the format:
```
admin_{admin_id}_{first_name}_{last_name}.png
```

## Troubleshooting

### Common Issues

1. **Stable Diffusion API Connection Error**
   - Ensure Automatic1111 is running with `--api` flag
   - Check that the Web UI is accessible at `http://127.0.0.1:7860`
   - Verify the model is loaded in Automatic1111

2. **OpenAI API Error**
   - Verify your OpenAI API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure the API key has access to GPT-4o

3. **JSON Parsing Error**
   - Verify JSON files exist in the `data/` directory
   - Check JSON syntax is valid
   - Ensure the data structure matches the expected format

4. **Image Generation Fails**
   - Check the model filename in `SD_MODEL_CHECKPOINT`
   - Verify the model is compatible with the specified dimensions (1024x1024)
   - Check Automatic1111 logs for specific errors

### Debug Mode

To see more detailed error information, you can modify the script to include additional logging or run with verbose output.

## File Structure

```
Stable image bot/
├── main.py                 # Main application script
├── config.py               # Configuration settings
├── db_utils.py             # Database utility functions
├── setup.py                # Setup and installation script
├── test_setup.py           # Test script for verification
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                   # JSON data directory
│   ├── universities/       # Category folders
│   ├── hospitals/         # Category folders
│   └── research_institutes/ # Category folders
├── profiles.db            # SQLite database (created automatically)
└── generated_images/      # Output directory (created automatically)
```

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Review the Automatic1111 documentation for API usage
4. Check OpenAI API documentation for prompt engineering best practices 