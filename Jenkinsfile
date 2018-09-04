pipeline {
  agent any
  stages {
    stage('One') {
      steps {
        echo 'This is cloning repo!!!'
      }
    }
    stage('Two') {
      steps {
        input('Do u want to proceed?')
      }
    }
  }
}  
    
