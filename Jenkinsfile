pipeline {
  agent any
  stages {
    stage('Build') {
      echo 'Building Now' 
    }
    stage('Test') {
      steps {
        input('Do you want to Continue?')
      }  
    }
    stage('Integration') {
      steps {
        echo 'Completed'
      }
    }
  }
}

    
