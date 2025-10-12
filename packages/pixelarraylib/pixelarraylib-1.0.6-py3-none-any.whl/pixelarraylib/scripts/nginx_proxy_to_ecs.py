import argparse
import base64
from pixelarraylib.system.common import execute_command_through_ssh
from pixelarraylib.aliyun.domain import DomainUtils


def nginx_proxy_file_template(
    domain_name: str, port_of_service: str, ssl_cert_path: str, ssl_key_path: str
) -> str:
    return f"""
server {{
    listen 80;
    server_name {domain_name}.pixelarrayai.com;

    # 将所有HTTP请求重定向到HTTPS
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl;
    server_name {domain_name}.pixelarrayai.com;

    ssl_certificate {ssl_cert_path};
    ssl_certificate_key {ssl_key_path};

    location / {{
        proxy_pass http://localhost:{port_of_service};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
    """


def add_a_record_to_dns(
    domain_name: str, ecs_ip: str, access_key_id: str, access_key_secret: str
) -> None:
    domain_utils = DomainUtils(
        access_key_id, access_key_secret, domain_name="pixelarrayai.com"
    )
    domain_utils.add_domain_record(
        rr=domain_name,
        type="A",
        value=ecs_ip,
    )
    print("域名解析记录添加成功")


def deploy(
    ecs_ip: str,
    domain_name: str,
    port_of_service: str,
    ssl_cert_path: str,
    ssl_key_path: str,
    access_key_id: str,
    access_key_secret: str,
) -> None:
    execute_command_through_ssh(
        ecs_ip,
        f"sudo rm -f /etc/nginx/sites-available/{domain_name} && sudo rm -f /etc/nginx/sites-enabled/{domain_name}",
    )
    print("删除原有配置成功")
    execute_command_through_ssh(
        ecs_ip,
        f"sudo touch /etc/nginx/sites-available/{domain_name}",
    )
    print("文件创建成功")
    nginx_proxy_file_content = nginx_proxy_file_template(
        domain_name, port_of_service, ssl_cert_path, ssl_key_path
    )
    # 使用 base64 编码来避免特殊字符问题
    encoded_content = base64.b64encode(nginx_proxy_file_content.encode('utf-8')).decode('utf-8')
    execute_command_through_ssh(
        ecs_ip,
        f"echo '{encoded_content}' | base64 -d | sudo tee /etc/nginx/sites-available/{domain_name} > /dev/null",
    )
    print("内容写入成功")
    execute_command_through_ssh(
        ecs_ip,
        f"sudo ln -s /etc/nginx/sites-available/{domain_name} /etc/nginx/sites-enabled/{domain_name}",
    )
    print("nginx配置添加成功，准备重启")
    execute_command_through_ssh(
        ecs_ip, f"sudo nginx -t && sudo systemctl restart nginx"
    )
    print("重启成功，请检查配置是否生效")
    add_a_record_to_dns(domain_name, ecs_ip, access_key_id, access_key_secret)


def main():
    parser = argparse.ArgumentParser(
        description="Nginx反向代理配置到ECS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--ecs_ip", "-e", help="服务IP地址")
    parser.add_argument("--domain_name", "-d", help="需要代理的域名")
    parser.add_argument("--port_of_service", "-p", help="端口或服务")
    parser.add_argument("--access_key_id", "-a", help="阿里云AccessKeyID")
    parser.add_argument("--access_key_secret", "-s", help="阿里云AccessKeySecret")

    args = parser.parse_args()

    deploy(
        args.ecs_ip,
        args.domain_name,
        args.port_of_service,
        "/var/pixelarray/ssl_auth/pixelarrayai.com.pem",
        "/var/pixelarray/ssl_auth/pixelarrayai.com.key",
        args.access_key_id,
        args.access_key_secret,
    )


if __name__ == "__main__":
    main()
