# Ansible Role: send_ip

This role collects active IPv6 addresses and system uptime, logs the info, and sends it to [Prowl](https://www.prowlapp.com/) via API.

## Requirements

- Python 3
- `pyprowl` module (installed via virtualenv)
- Ansible 2.11+

## Role Variables

| Variable         | Description                         | Required |
|------------------|-------------------------------------|----------|
| `prowl_api_key`  | Your Prowl API key (Vault-friendly) | ✅ Yes   |

## Example Playbook

```yaml
- hosts: all
  become: true
  vars_files:
    - vault.yml

  roles:
    - pbertain.send_ip
```

## Vault Example

```bash
ansible-vault create vault.yml
```

```yaml
prowl_api_key: "your_secret_key"
```

## License

MIT

## Author Information

This role was created by ChatGPT and Paul Bertain.
