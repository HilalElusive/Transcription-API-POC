terraform {
  backend "s3" {
    bucket  = "tf-state-hilal-letter-transcription"
    key     = "letter-transcription/poc/terraform.tfstate"
    region  = "eu-west-3"
    encrypt = true
  }
}