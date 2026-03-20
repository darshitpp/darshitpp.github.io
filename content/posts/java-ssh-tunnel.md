---
title: "SSH Tunnelling with Java"
date: 2024-09-21T16:10:34+05:30
draft: false
tags: [ "ssh", "java", "access", "remote", "localhost", "jumphost"]
comments: true
description: "What to do when you have no local access to a remote resource"
cover:
    image: "img/java-ssh-tunnel/SSH Tunnel.png" # image path/url
    alt: "SSH Tunneling diagram" # alt text
    relative: false # when using page bundles set this to true
    hidden: false # only hide on current single page
---

You heave a sigh of relief, as the QA has approved a long-awaited feature for deployment on Prod. However, as a part of the process, it is first deployed on the UAT env, where there are test accounts that can be used to certify the feature works outside of the local developer and QA testing systems. 

But... running the test suite results in a lot of failures!

---
*Reply with the always relevant "But it works on my machine!"*

What do you do? You're _sure_ that the code works. Defintely sure. Maybe the problem is with the UAT environment then? But what could be the problem with the environment? Maybe the test accounts which are newly created, are configured incorrectly? Probably yes, you think. You have access to the logs for the environment, but the scenario which it is failing for, has limited to no logs to identify the problem. You internally curse your ancestral developers.

Another option? Remote debugging! While this is a good idea, it is seldom practical for environments where the apps are under constant use. If your code is in the "hot path", good luck figuring out what requests are yours. Also it may slow down the app significantly.

Essentially, what you want is to debug the application, as if it was deployed on your local machine, but the database of the UAT server. But since UAT server is not *directly* accessible to your local application, you're out of luck.

Or are you? Fret not, because an SSH Tunnel is here to your rescue.


### SSH Tunnel

What is an SSH Tunnel? And how do I use it?

Short answer:

SSH Tunneling will allow your application to behave as if it is deployed on a remote system, through which the UAT database is accessible.

Long answer:

The Linux `ssh` command provides a functionality to "port forward". Admittedly, the term "port forward" is pretty non-descriptive. Hence, I'll let StackOverflow provide to you a detailed, and a far easier explanation of SSH Tunneling than what I can here. You can read it here: https://unix.stackexchange.com/a/115906. I recommend you to read the answer because it has diagrams that are far easy to understand than the text based answers.

However, I'll still copy the relevant sections here.
> ```bash
> ssh -L 123:farawayhost:456 remotehost
> ```
> local: `-L Specifies that the given port on the local (client) host is to be forwarded to the given host and port on the remote side.`
> `ssh -L sourcePort:forwardToHost:onPort connectToHost` means: connect with ssh to `connectToHost`, and forward all connection attempts to the ***local*** `sourcePort` to port `onPort` on the machine called `forwardToHost`, which can be reached from the `connectToHost` machine.

#### Example

For our use case, our sample command will be:

```bash
ssh -L <Local Port>:<UAT Database IP>:<UAT Database Port> <JumpHost IP>
```

Note, here the `JumpHost` is a system which can connect to `<UAT Database IP>` with the port `<UAT Database Port>`.

Once we have this figured out, everything else is a cakewalk!

You can simply run the command, and you'll be able to access the UAT Database on your `localhost:<Local Port>`. Almost feels like magic!

If you need to connect to multiple databases, you will need to run this command multiple times. Or you can write a bash script which can dynamically read a config file to open multiple SSH Tunnels.

I, being a Java programmer, would rather deal with statically compiled Java code, than worry about a dynamically typed language like bash. So, I utilized the [`jsch`](https://github.com/mwiede/jsch) library to whip up an extensible project, which creates and maintains multiple SSH Tunnels. You can check it out here: https://github.com/darshitpp/java-ssh-tunnel


### Structure
```bash
java-ssh-tunnel
└── src
    └── main
        ├── java
        │   └── dev
        │       └── darshit
        │           └── java_ssh_tunnel
        │               ├── Main.java
        │               ├── MultiTunneler.java
        │               ├── Tunneler.java
        │               └── ssh
        │                   ├── TunnelDetails.java
        │                   └── UserDetails.java
        └── resources


```

### Usage

1. Download the project
2. Load up in your IDE
3. Run `mvn clean install`
4. Change `Main.java` with required details like SSH `username`, SSH `password`, JumpHost `sshHost`
5. (Optional) Maybe load up `localPort`, `remoteHost`, and `remotePort` details from a file
6. Run `Main.java`

If all things go well, you'll see the following output on your `stdout`
```
Starting tunneling...
<remoteHost>:<remotePort> is available on localhost:<localPort>
Press Enter to terminate the tunnels...
```

### Caveats

While the above is very convenient, ***DO NOT USE IT TO CONNECT TO PROD***. Yes, that had to be written in bold with emphasis. Shall I print the message to `stderr` too? Comment below.

