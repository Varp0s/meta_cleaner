# File Cleaner API

![File Cleaner API](/images/api_cleaned.png)

This project provides an API for uploading files and cleaning metadata from them. Supported file types include `.doc`, `.docx`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.gif`,
I would appreciate if you test it and give me feedback, until then stay healthy!

## Installation
Change env.template to env after cd env change .env.template to .env 
1. Clone the repository:
    ```sh
    git clone https://github.com/Varp0s/meta_cleaner
    cd meta_cleaner
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Run a FastAPI:
    ```sh
    uvicorn main:app --reload
    ```    

## Docker Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Varp0s/meta_cleaner
    cd meta_cleaner
    ```
2. Run docker compose:
    ```sh
    docker-compose up -d --build
    ```
3. Run a Browser:
    ```sh
    go to http://127.0.0.1:8000
    ```
## Use Single

Download this repo install requirements, after run a script. example ussage: python3 single.py {file}

## API Endpoints

### POST /upload_file/

- **Description**: Upload a file to be cleaned.
- **Request**: `multipart/form-data` with a file field.
- **Response**: JSON with the original filename and the path to the cleaned file.

## Environment Variables

- `UPLOAD_DIR`: Directory where uploaded files will be stored.
- `CLEANED_DIR`: Directory where cleaned files will be stored.

## TO:DO

Add archive metadata clen endpoit

## Dependencies

- `fastapi`
- `uvicorn`
- `python-dotenv`

## License

This project is licensed under the MIT License.
