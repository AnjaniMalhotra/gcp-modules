@echo off
REM Topic 5 - API Gateway: deploy a public, API-key-protected front door
REM for digest-worker-http.
REM Requires: 04_cloud_tasks_setup.bat already run (digest-worker-http
REM deployed), and 05_openapi_spec.yaml edited to have the real function
REM URL in place of WORKER_HTTP_URL_HERE.

echo == creating the logical API ==
gcloud api-gateway apis create %API_ID%

echo == creating an API config from the OpenAPI spec ==
gcloud api-gateway api-configs create %API_CONFIG_ID% ^
  --api=%API_ID% ^
  --openapi-spec=05_openapi_spec.yaml ^
  --backend-auth-service-account=%WORKER_SA_EMAIL%

echo == deploying the gateway ==
gcloud api-gateway gateways create %GATEWAY_ID% ^
  --api=%API_ID% ^
  --api-config=%API_CONFIG_ID% ^
  --location=%REGION%

echo.
echo == creating an API key ==
gcloud services api-keys create --display-name="Digest API Key"
echo Copy the "keyString" from the output above (or run:
echo   gcloud services api-keys list
echo   gcloud services api-keys get-key-string KEY_ID
echo to retrieve it).

echo.
echo == getting the gateway hostname ==
gcloud api-gateway gateways describe %GATEWAY_ID% --location=%REGION% --format="value(defaultHostname)"

echo.
echo Test it (replace GATEWAY_HOSTNAME and YOUR_API_KEY):
echo   curl "https://GATEWAY_HOSTNAME/trigger-digest?key=YOUR_API_KEY"
echo No identity token anywhere in that command - that's the point of this topic.
