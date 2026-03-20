---
title: "Handling limited sudo access through Ansible"
date: 2024-03-29T18:52:27+05:30
draft: false
tags: [ "devops", "ansible", "sudo", "python", "password", "nopasswd", "root", "sudoers"]
comments: true
description: "Especially useful if you don't have root access or access to the sudoers file"
---

---

### Running specific commands with sudo using Ansible

It seems a trivial use case, but it's not. Consider a situation when you're not the user allowed a full sudo access on the remote machine. However, you are only allowed the sudo access on certain commands, which, of course, requires a password. For example, starting or stopping a service.

Ansible allows privilege escalation, but that will not solve your problem because:

1. Elevated access is changed to the user `root` by default
2. Elevated access requires a password, i.e. password for the `root` user

You obviously don't have access to the root user.

There are a couple of other directives you can use, which the [ansible doc](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_privilege_escalation.html#become-directives) makes it hard to understand even though it tries to be simple in language. You can try to use the `ansible_become_user` to change to another user while escalating the privilege besides `root`. However, if you are already the user who has the sudo command access, this will not help.

If you have access to change (or get changed) the `/etc/sudoers` file, you can change the sudo command to be run through `NOPASSWD`. 

If you are here, it is likely that you do not have the permissions to change the `sudoers` file either.

---

### Resolution

I saw a couple of workarounds mentioned across Github[^1], StackOverflow[^2], and Reddit[^3][^4], but they were outdated, and didn't work for me.

One of the solution[^5] suggests to use `sudo` with `-S` and `echo` the password from the terminal. This will, however, probably leak your password on the shell, and we don't want this, do we?

However, is there a way Ansible can input the password to `sudo`? Yes! Perhaps we can use something like the `-y` flag that is often used to skip prompts of `yes/no` on the terminal. Thankfully, Ansible is built over Python, and most Python modules are available within Ansible. "How does that help?", you ask. Python has a very helpful module called [`pexpect`](https://pexpect.readthedocs.io/en/stable/). Similarly, Ansible has [`expect`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/expect_module.html).


```yaml
- name: Stop service
  ansible.builtin.expect:
    command: "sudo systemctl stop service"
    responses:
      (?i)password: "{{ pass }}"
  no_log: true
```

This solves our problem! We can load this password through Ansible vault, and pass it in without being logged anywhere! We also do not have to rely on having access or permissions through the `/etc/sudoers` file, saving a lot of headache of trying to get approvals.


[^1]: [Problem: Can't use sudo command-limiting in Ansible](https://gist.github.com/nanobeep/3b3d614a709086ff832a)
[^2]: [Specify sudo password for Ansible](https://stackoverflow.com/questions/21870083/specify-sudo-password-for-ansible)
[^3]: [How do I run sudo commands with another user](https://www.reddit.com/r/ansible/comments/vbbhpj/how_do_i_run_sudo_commands_with_another_user/)
[^4]: [Become sudo with limited sudo privileges](https://www.reddit.com/r/ansible/comments/nmpbv5/become_sudo_with_limited_sudo_previleges/)
[^5]: [Hack using Ansible `raw`](https://gist.github.com/nanobeep/3b3d614a709086ff832a?permalink_comment_id=2619975#gistcomment-2619975)