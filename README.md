# APIGateway

This is the APIGateway that provides access to public endpoints from services. also provides authorization. run the app and go to `/docs` to see the endpoints

## Running the service

Make a `.env` file in the root directory and create the variables where `<VAR>` should be replaced with actual values:
```python
JWT_SECRET=<SECRET>
JWT_ALG=<ALG>
EXPIRE=<EXP>
CLIENT=<<PROTOCOL>://IP:PORT>
<XXXX_SERVICE>=<<PROTOCOL>://IP:PORT>

```

remember to run the services at another port than the apigateway, if runnig on the same machine.
### Running in docker

Creating docker container and running the app:
```sh
docker build -t apigateway .
docker run -p 8443:8443 apigateway
```

### Development

run this in powershell:

```sh
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
```

on macOS/Linux you might need to do `source .venv\Scripts\activate` and `.venv/Scripts/activate.bat` in windows CMD