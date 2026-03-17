# Deploy da API — Passo a Passo

## Railway
1. Instale: npm install -g @railway/cli
2. railway login
3. cd django_backend
4. railway init
5. railway add --database postgresql
6. Configurar variáveis: SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS
7. railway up

## Render
1. Crie conta em render.com
2. New > Web Service > conecte o repositório
3. Root directory: django_backend
4. Build: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
5. Start: gunicorn config.wsgi --workers 2
6. Adicionar PostgreSQL: New > PostgreSQL, copiar DATABASE_URL
7. Configurar variáveis de ambiente conforme .env.example

## Modelos de ML
Os arquivos models/face_landmarker.task e models/face_recognition_sface_2021dec.onnx
precisam estar disponíveis no servidor. Opções:
- Incluir no repositório (aumenta ~50MB no slug)
- Hospedar em S3/R2 e baixar no build step
Recomendado para início: incluir no repositório com git-lfs ou diretamente.

## Nota sobre tamanho de build (Railway/Render free)
Dependências como mediapipe e opencv-contrib-python-headless são pesadas e podem aumentar bastante
tempo/tamanho de build em planos gratuitos. Caso o build falhe por limite de recursos, alternativas:
- Garantir uso de opencv-contrib-python-headless (já aplicado) em vez de opencv com GUI.
- Fixar versões compatíveis e evitar dependências extras não essenciais.
- Migrar para plano com mais RAM/CPU/disco temporário durante build.
- Pré-compilar artefatos em imagem Docker própria para reduzir variabilidade de build.
