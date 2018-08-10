pipeline {
  agent any
  stages {
    stage('one') {
      echo 'Building Now'
    }
    stage('two') {
      input('Do you want to proceed?')
    }
    stage('three') {
      steps {
        git clone "https://github.com/Poonammahunta/hello_world.git"
      }
    }
  }
}  
    
