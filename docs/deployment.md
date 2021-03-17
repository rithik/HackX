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

## Active Migration Guide of Databases

From Heroku-managed Database to AWS RDS, use the following steps to migrate.

1. `heroku maintenance:on`

2. `heroku pg:backups:capture`

3. `heroku pg:backups:download`

4. `pg_restore --verbose --clean --no-acl --no-owner -h HOST_URL -U USERNAME -d DATABASE_NAME DUMP_FILE`

5. Ensure AWS version is working.

6. Change `DATABASE_URL` in Heroku
