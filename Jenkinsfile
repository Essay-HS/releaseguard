pipeline {
  agent any
  environment {
    VENV = "${WORKSPACE}/.venv"
    TWILIO_DRY_RUN = 'false'
  }
  stages {
    stage('Install') { steps { sh 'python3 -m venv "$VENV" && "$VENV/bin/pip" install -r requirements.txt' } }
    stage('Test') { steps { sh 'mkdir -p reports && "$VENV/bin/pytest" --junitxml=reports/pytest.xml --cov=app' } post { always { junit 'reports/pytest.xml' } } }
    stage('Deploy') { when { expression { return env.DEPLOY_COMMAND?.trim() } } steps { sh env.DEPLOY_COMMAND } }
    stage('Production Health Check') { when { expression { return env.HEALTHCHECK_URL?.trim() } } steps { sh '"$VENV/bin/python" scripts/health_check.py' } }
  }
  post {
    success { withCredentials([string(credentialsId: 'releaseguard-api-token', variable: 'BUILD_API_TOKEN'), string(credentialsId: 'twilio-account-sid', variable: 'TWILIO_ACCOUNT_SID'), string(credentialsId: 'twilio-auth-token', variable: 'TWILIO_AUTH_TOKEN'), string(credentialsId: 'twilio-from-number', variable: 'TWILIO_PHONE_NUMBER'), string(credentialsId: 'alert-phone-number', variable: 'ALERT_PHONE_NUMBER')]) { sh '"$VENV/bin/python" scripts/record_build.py SUCCESS'; sh '"$VENV/bin/python" scripts/send_twilio_alert.py SUCCESS' } }
    failure { withCredentials([string(credentialsId: 'releaseguard-api-token', variable: 'BUILD_API_TOKEN'), string(credentialsId: 'twilio-account-sid', variable: 'TWILIO_ACCOUNT_SID'), string(credentialsId: 'twilio-auth-token', variable: 'TWILIO_AUTH_TOKEN'), string(credentialsId: 'twilio-from-number', variable: 'TWILIO_PHONE_NUMBER'), string(credentialsId: 'alert-phone-number', variable: 'ALERT_PHONE_NUMBER')]) { sh '"$VENV/bin/python" scripts/record_build.py FAILED || true'; sh '"$VENV/bin/python" scripts/send_twilio_alert.py FAILED || true' } }
  }
}

