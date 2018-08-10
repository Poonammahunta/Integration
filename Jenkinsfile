pipeline {
  agent any
  stages {
    stage('Build') {
      echo 'Building Now'
    }
    stage('Test') {
      input('Do you want to proceed?')
    }
    stage('Artifact') {
      steps {
        git clone "https://github.com/Poonammahunta/hello_world.git"
      }
    }
  }
}  
    
