// Sample Declarative Jenkinsfile for the 5 QA pipelines.
// Place this at the root of your repo alongside the .py files below.
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'python3 -m pip install --user pytest'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m pytest \
                        LoanProcessingQA.py \
                        OrderManagementQA.py \
                        HospitalManagementQA.py \
                        AirlineReservationQA.py \
                        ParkingQA.py \
                        --junitxml=results.xml -v
                '''
            }
        }
    }

    post {
        always {
            junit 'results.xml'
        }
    }
}
