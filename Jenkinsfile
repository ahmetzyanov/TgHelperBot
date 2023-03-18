pipeline {
  agent {
    kubernetes {
      cloud 'kubernetes'
      defaultContainer 'docker'
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: "registry.gitlab.com/ahmetzyanov/buildcontainer"
    command: ['cat']
    tty: true
    volumeMounts:
    - name: dockersock
      mountPath: /var/run/docker.sock
    privileged: true
  volumes:
  - name: dockersock
    hostPath:
      path: /var/run/docker.sock
  imagePullSecrets:
  - name: gitlab-cred
"""
    }
  }
  stages {
    stage('Notify about started job') {
      steps {
        telegramSend """🕘 **Started job** 🕘```
${env.BUILD_TAG}
Build: ${env.BUILD_URL}
Job: ${env.JOB_URL}```"""
      }
    }
    stage('Git clone kubernetes configs') {
      steps {
        script {
          withCredentials([string(credentialsId: 'tg_tghelperbot_token', variable: 'TOKEN')]) {
            sh("sed -i 's/tg_tghelperbot_token/$TOKEN/' vars/credentials.py")
          }
          withCredentials([string(credentialsId: 'cloudflare_token', variable: 'TOKEN')]) {
            sh("sed -i 's/cloudflare_token/$TOKEN/' vars/credentials.py")
          }
          withCredentials([string(credentialsId: 'gmail', variable: 'EMAIL')]) {
            sh("sed -i 's/gmail/$EMAIL/' vars/credentials.py")
          }
          withCredentials([string(credentialsId: 'tghelperbot_whitelist', variable: 'WHITELIST')]) {
            sh("sed -i 's/WHITELIST/$WHITELIST/' vars/credentials.py")
          }
        }
      }
    }
    stage('Build Docker image') {
      steps {
        container('docker') {
          script {
            try {
              def image = docker.build("registry.gitlab.com/ahmetzyanov/tghelperbot:${env.BUILD_ID}")
              docker.withRegistry('https://registry.gitlab.com/ahmetzyanov/tghelperbot',
                                  'bf0f34f6-1424-44c9-9d1b-e174987fb4e7') {
                image.push()
                image.push('latest')
              }
            } catch (Exception e) {
              telegramSend "❌ Unseccessfull TgHelperBot build ❌ ```Job tag: ${env.BUILD_TAG}```"
              error "TgHelperBot build error"
            }
          }
        }
      }
    }
    stage("Deploy to Kubernetes") {
      steps {
        script {
          try {
            withKubeConfig([
              credentialsId: '9d745e97-be47-495b-ab80-232de01122e3',
              serverUrl: "https://${env.KUBERNETES_SERVICE_HOST}:443"]) {
              sh("sed -i 's/BUILD_ID/${env.BUILD_ID}/g' tghelperbot_deployment.yaml")
              sh("kubectl apply -f tghelperbot_deployment.yaml")
            }
          } catch (Exception e) {
            telegramSend "❌ Unseccessfull TgHelperBot deployment ❌ ```Job tag: ${env.BUILD_TAG}```"
            error "TgHelperBot deployment error"
          }
        }
      }
    }
    stage("Check if deployment successful") {
      steps {
        script {
          try {
            withKubeConfig([
              credentialsId: '9d745e97-be47-495b-ab80-232de01122e3',
              serverUrl: "https://${env.KUBERNETES_SERVICE_HOST}:443"]) {
                sh("kubectl rollout status deployment.apps/tghelperbot-depl -n jenkins")
                sh("kubectl wait --for=condition=available --timeout=60s deployment.apps/tghelperbot-depl")
            }
          } catch (Exception e) {
            telegramSend "❌ TgHelperBot deployment error ❌ ```Job tag: ${env.BUILD_TAG}```"
            error "TgHelperBot deployment error"
          }
        }
      }
    }
    stage("Telegram notification on success") {
      steps {
        script {
          telegramSend "✅ Successfully finished job ✅ ```${env.BUILD_TAG}```"
        }
      }
    }
  }
}