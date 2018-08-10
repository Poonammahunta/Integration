pipeline {
  agent any
  stages {
    stage('one') {
      steps {
        echo 'Building Now'
      }  
    }
    stage('two') {
      steps {
        input('Do you want to proceed?')
      }  
    }
    stage('three') {
      steps {
        echo 'Completed'
      }
    }
  }
}

    
