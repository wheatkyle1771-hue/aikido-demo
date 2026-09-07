# Not meant to be applied - Aikido's IaC scanner reads this file
# directly. Live version of the IAM/role finding is in ../../cloud/aws
# instead.

resource "aws_s3_bucket" "demo" {
  bucket = "aikido-demo-bucket"
}

# Public read AND write.
resource "aws_s3_bucket_policy" "demo_public" {
  bucket = aws_s3_bucket.demo.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadWrite"
      Effect    = "Allow"
      Principal = "*"
      Action    = ["s3:GetObject", "s3:PutObject"]
      Resource  = "${aws_s3_bucket.demo.arn}/*"
    }]
  })
}

# Wide open to the internet, all ports.
resource "aws_security_group" "demo_open" {
  name        = "aikido-demo-allow-all"
  description = "Wide open on purpose, for the Aikido demo"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Public, unencrypted, hardcoded password - three problems in one resource.
resource "aws_db_instance" "demo" {
  identifier             = "aikido-demo-db"
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_name                = "appdb"
  username               = "admin"
  password               = "Sup3rSecretProdPassword!"
  publicly_accessible    = true
  storage_encrypted      = false
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.demo_open.id]
}
