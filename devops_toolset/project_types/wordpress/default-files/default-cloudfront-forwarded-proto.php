// AWS Cloudfront
if (isset($_SERVER['HTTP_CLOUDFRONT_FORWARDED_PROTO']) &&
    $_SERVER['HTTP_CLOUDFRONT_FORWARDED_PROTO'] === 'https')
{
    $_SERVER['HTTPS'] = 'on';
}
