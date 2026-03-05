# Task & dialog
Jenkins → GitHub Actions (Agentic Loop)

Build a small program that converts a Jenkins pipeline (Jenkinsfile) into a GitHub Actions workflow using an LLM and iterates using a simple converter <-> reviewer loop.
Use any language and any agentic framework. Keep it practical and minimal.
You are expected to use your own LLM access: a local LLM should be used via LM Studio (note: the given Windows 11 PC has 12 GB VRAM available).
No endpoints or credentials will be provided.

## What to Build:
- A converter that reads a Jenkinsfile and produces a GitHub Actions workflow YAML.
- A reviewer that inspects the generated workflow and either approves it or requests changes.
- A loop where the converter can improve the workflow based on the reviewer’s feedback.

## Inputs
Two Jenkinsfiles are provided. Your program should be able to run on either.

## Output
Write the final workflow(s) to disk.

# Case presentation
You must prepare a pitch of approximately 10–15 minutes, where you go through your design, cover the discussion questions, and explain the reasoning behind your decisions and considerations. The participants in your pitch will be the team’s leader, an HR representative, and 1–2 people from the team.
A total of up to 45 minutes has been allocated for the case review including discussion, but you do not need to use all the time.

## presentation
Pitch your design solution where you go through the general architectural choices, for example with a diagram.
Please go through any code – demonstrate parts of the code if possible.

## Reflection and priority
Present your choices – What are the biggest advantages and disadvantages – are there alternatives to the chosen design?
Discuss possible extensions and improvements to your design.

## Perspective
Discuss your solution from a broader organizational perspective. Could your solution be expanded to other technologies or applied elsewhere?
How would you enable others to work with Agentic AI?

# Jenkinsfiles

## Jenkinsfile 1
```
pipeline {
  agent any
  environment {
    APP_ENV = "ci"
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Build') {
      steps {
        sh './gradlew --no-daemon clean build'
      }
    }
    stage('Test') {
      steps {
        sh './gradlew --no-daemon test'
      }
      post {
        always {
          junit 'build/test-results/test/*.xml'
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'build/libs/*.jar', fingerprint: true
    }
  }
}
```

## Jenkinsfile 2
```
pipeline {
  agent {
    docker {
      image 'gradle:8.7.0-jdk17-alpine'
      args '-u root'
    }
  }
  environment {
    APP_ENV = "ci"
  }
  options {
    timestamps()
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Prepare Tools') {
      steps {
        sh 'apk add --no-cache bash git jq'
        sh 'jq --version'
      }
    }
    stage('Build') {
      steps {
        sh './gradlew --no-daemon clean build'
      }
    }
    stage('Tests') {
      parallel {
        stage('Unit Tests') {
          steps {
            sh './gradlew --no-daemon test'
          }
          post {
            always {
              junit 'build/test-results/test/*.xml'
            }
          }
        }
        stage('Lint') {
          steps {
            sh './gradlew --no-daemon check'
          }
        }
      }
    }
    stage('Publish Artifacts') {
      when {
        branch 'main'
      }
      steps {
        echo 'Publishing artifacts (placeholder)'
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'build/libs/*.jar', fingerprint: true
    }
  }
}
```