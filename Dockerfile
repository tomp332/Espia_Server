# ---- Base python ----
FROM python:3.9-alpine3.14 AS base
# Create app directory
WORKDIR /server

# ---- Dependencies ----
FROM base AS dependencies  
COPY requirements.txt ./
# install app dependencies
RUN pip install -U pip
RUN apk update && apk add python3-dev gcc libc-dev
RUN apk add --no-cache nss
RUN pip install -r requirements.txt

# ---- Copy Files/Build ----
FROM dependencies AS build  
WORKDIR /server
COPY espia_server /server/espia_server

# --- Release with Alpine ----
FROM python:3.9-alpine3.14 AS release
# Create app directory
WORKDIR /server

COPY --from=dependencies /server/requirements.txt ./
COPY --from=dependencies /root/.cache /root/.cache

# Install app dependencies
RUN pip install -U pip
RUN apk update && apk add python3-dev gcc libc-dev
RUN apk add --no-cache nss
RUN pip install -r requirements.txt
COPY --from=build /server/ ./
CMD ["python","-m","espia_server"]
