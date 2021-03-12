# Steps to Deploy onto AWS

## Elastic Beanstalk

1. `eb create ENV_NAME`

2. Add Configuration Variables
[https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl.html](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-ssl.html)

3. Create a new certificate through AWS ACM.

4. Follow instructions to add CNAME to verify domain.

5. Add port forwarding from 443 to 80 with the new certificate.

## Update version

`eb deploy --staged -v`
