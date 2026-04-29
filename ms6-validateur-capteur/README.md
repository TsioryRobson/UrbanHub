# ms6-validateur-capteur

Microservice FastAPI de validation et classification des donnees capteur.

## Endpoints

- `GET /health`: verifie que le service repond.
- `GET /thresholds`: liste les seuils configures.
- `POST /validate`: classe une mesure capteur.

Exemple:

```json
{
  "sensor": "c02",
  "value": 500.0
}
```

Reponse:

```json
{
  "valid": true,
  "level": "normal",
  "sensor": "c02",
  "threshold": 800.0,
  "timestamp": "2026-04-27T05:30:00.000000+00:00"
}
```

## Seuils

| Capteur | Seuil modere | Seuil critique | Unite |
| --- | ---: | ---: | --- |
| c02 | 800 | 1000 | ppm |
| temperature | 35 | 40 | degC |
| noise | 70 | 85 | dB |
| pm25 | 25 | 50 | ug/m3 |
| humidity | 60 | 80 | % |

## Lancement local

```bash
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8006
```

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
