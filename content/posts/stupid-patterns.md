---
title: "Stupid Patterns"
date: 2021-12-31T19:00:26+05:30
draft: false
cover:
  image: "https://images.pexels.com/photos/60504/security-protection-anti-virus-software-60504.jpeg"
tags: ["stupid patterns", "dark patterns", "cyber-security", "ui/ux", "product managers"]
comments: true
description: "Stupid patterns on the web (and how to prevent your bank account from getting hacked)"
---

We know about companies using [Dark Patterns](https://www.shopify.com/partners/blog/dark-patterns) (more on this post by TechCrunch: [WTF is dark pattern design?](https://techcrunch.com/2018/07/01/wtf-is-dark-pattern-design/)), and how they affect users. But can there be something like a "Stupid Pattern"? A thing that most companies do, and they don't even realize it's stupid? This blog post is a part real-life case study, and a major rant about one such pattern that is almost definitely, very stupid.

It's mostly a rant, though I encourage you to read how it came to be that way.

----


### Gazon Communications/Razorpay

My first experience of a "stupid pattern" was with Gazon Communications and RazorPay. Gazon is an internet provider, and RazorPay is a payments processor. In May 2019, I received the following email:

{{<figure src="/img/stupid-patterns/Gazon Welcome Email.png" caption="Gazon Welcome Email">}}

The plaintext password notwithstanding, the email surprised me because I definitely did not sign up for it. I received an additional email with an invoice for the payment.
{{<figure src="/img/stupid-patterns/Gazon Payment Invoice.png" caption="Gazon Payment Invoice">}}

Yes, the email provided in the invoice is mine, but the name and the address do not match (obviously)! I assumed it to be just another typo by the user during the registration/signing up. I thought it would be best to ignore it. These typos happen, and assumed that when the user realized their mistake, they would promptly go correct it.

I was wrong. The user never realized the "mistake". I received more such emails in the following months.

Fed up, I contacted the phone number mentioned in the original invoice. 

{{<figure src="/img/stupid-patterns/Darshit Dave WhatsApp Gazon.png" caption="WhatsApp chat with my alter ego">}}

The person was clueless. I reached out to him in January 2020, but routinely received emails till May 2020.

{{<figure src="/img/stupid-patterns/Gazon Emails.png">}}

I never received any further emails because the user probably never recharged his internet subscription.

This wasn't even a spam email!

----

### Bigbasket

Bigbasket is one of the major Indian e-commerce companies, catering to delivering fresh vegetables, and other edibles. I did have an account with them, but did not buy anything when I created the account. All of a sudden, 3 years later, I start receiving emails with OTPs, and even a recharge receipt!

{{<figure src="/img/stupid-patterns/Bigbasket recharge.png" caption="Thank you Bigbasket for free credits!">}}
{{<figure src="/img/stupid-patterns/Bigbasket Emails.png">}}

Someone just used my email on their account, and Bigbasket didn't even care to verify if the email indeed belonged to them! I also received their phone number in one of the emails. This time, I decided to not contact the person, and instead directly reached out to Bigbasket to close/delete the account. It took 15 emails to even try to explain them the problem. They did not understand, and the issue, to this date, remains unresolved. My account still exists on the platform, and is not deleted yet, despite repeated requests.

----

### Wish.com

To be honest, I did not even know about this site until I received the email of me "Signing up" on their website.
Moreover, the email looked like obvious spam.

{{<figure src="/img/stupid-patterns/Wish Email.png" caption="Nikl (probably a Nickelback fan)">}}

It was ridiculous! Even the name did not match this time! I reset the password of the Wish.com account (did not click any link in the email), and noticed that the person had ordered a couple of items. I immediately cancelled the order. The good thing is, they also have an option of deleting the account, and I did so. I was genuinely puzzled now. Was my email so common and prone to typos? It didn't seem likely because it's not even the usual format of `firstName.lastName`. Weird!!

----

### Pantaloons

It's now going too far. Pantaloons is a major garment retailer in India, and I had apparently shopped at one of their stores in Ahmedabad.

{{<figure src="/img/stupid-patterns/Pantaloons Invoice Email.png" caption="My Alter Ego on a Shopping spree">}}

This time I decided to click on the link in the email. The email wasn't a spam one, and to my surprise, it opened up with details of the order!

{{<figure src="/img/stupid-patterns/Pantaloons Invoice Link.png" caption="darshit kanshara buying trousers on Pantaloons">}}

The page also had a link for "Completing my profile". I clicked on the link, and see what I find:

{{<figure src="/img/stupid-patterns/Darshit Kanshara Pantaloons Profile.png" caption="darshit kanshara's profile">}}

I now had his name, phone number, and date of birth! If I was enterprising and a "hacker" enough, I could even find a way to scam him out of some money. This was a one off invoice payment, and there was no "Unsubscribe" button, so I couldn't even "report" it to someone. I decided to not bother poor Darshit Kanshara with my email troubles.

----

### Jio

Jio is a mobile carrier, credited with disrupting the market with very cheap internet plans. I am already a customer, and so I was very surprised when I received another email linking my email to another phone number (not mine). 

{{<figure src="/img/stupid-patterns/Jio Emails.png" caption="Emails from Jio">}}

I was livid now. How can multiple people make mistakes in their email, especially when my name itself is not very common?!
Do notice the last email in the above screenshot, dated 02/07/2018. It says my email has been verified, but it's been verified with a different phone number that's actually mine. Jio probably already thought my email is verified, and linked it to another number without any verification!

I deactivated the SIM card. The person re-activated it. There was also no other way to change email except an OTP to the linked number!

----

### RBL Bank/Bajaj-Finserv Bank

The above emails were pretty random. Imagine my surprise when I received an email from a Credit Card company/Bank!

{{<figure src="/img/stupid-patterns/RBL Emails.png" caption="RBL Bank being large hearted and sharing Credit Card PINs">}}

The above emails have Credit Card application forms, and PINs. Though, the PDFs are in an encrypted format. How is the encryption, you ask?

I'll let one of the emails answer you.

{{<figure src="/img/stupid-patterns/RBL PDF Password.png" caption="How complicated can it be?">}}

All it takes to access the password protected form is a 10 character password. But is it really a 10 character password? I already know the characters of my name. How hard is it to get the date of birth? It's a simple 30 line python script. How had the person missed noticing no email statements or PIN for the Credit Card?

I decided to "crack"/"hack" the PDF, and contact the person. It took me just 15 mins to decrypt the PDF. I reached out to the guy, and he, like others earlier, had no clue about the wrong email!

{{<figure src="/img/stupid-patterns/Darshit Panchal RBL.png" caption="speechless...">}}

This was bonkers! Some person actually mistyped his whole email (and both of ours don't have a similarity except the first name). If I wanted, I could actually decrypt the document with the PIN, and hack all accounts of the said person. Decrypting merely the application form gave me the address, phone number, and other personal information. In the hands of a malicious agent, the said person could be looking at a potential ruin to their whole life savings, and identity theft.

And most companies don't even care to validate the "KYC".

If you thought this was enough confusion, I received another email yesterday...

----

### Booking.com

Some good samaritan booked a room with King sized bed for me in Hyatt Regency Toronto, for 15 days in March 2022!

{{<figure src="/img/stupid-patterns/Booking Emails.png" caption="#Lucky">}}

Again, the actual name is not mine (except the first name). He booked it for 15 days with it amounting to more than $3K CAD. How lucky (or unlucky) I am!	
{{<figure src="/img/stupid-patterns/Booking confirmation.png" caption="#Blessed">}}

I actually again contacted Booking.com through their helpline number. I already had the confirmation number and the PIN associated with the booking. The customer support instead asked me to confirm my name, which I replied to. They said that the name matches, and then asked me if I wanted to cancel the booking if I want. What!? They continued that as I had the confirmation number and the PIN, and even the name matched (only the first name, mind you), I would be able to cancel a booking worth more than $3K CAD. 

I questioned about how they sent me an email without confirming it was indeed me booking the hotel, they replied that it's the concern of the person booking the hotel/room! "No company provides the email verification service", they said, and if I had so much of a problem with the emails, I could just unsubscribe. That's *obviously* not the point I'm trying to make!

Imagine the whole internet running on an element of "trust", and no verification! This is what I call a "Stupid Pattern". It's not a Dark Pattern, but the chink in the armour will make internet users fail all around. All the point of digital security fails when someone mistypes their email, or someone else does. Why hasn't someone not even thought of this? Product Managers? All the people stressing on UI/UX?

A solution would be mandatory verification of emails, and as described above, not many companies do that. Even verification of emails has its problems. A typo to the email, may lead to a malicious actor "confirming"/"verifying" the email, and there goes your bank account. Now think about how many people use the internet, and don't know about basic online safety measures like a strong password, or ad-blockers, encountering something like this? And potentially on the wrong side of things!

I have thought about what is it about my email that leads to me getting legitimate emails like the above. I'm sure you're now thinking about it too. But I've never found a satisfactory answer, because an email is not inherently "secret" like a password is. There is no problems with emails "leaking" out, unlike passwords. And I can only hope someone is not getting *my* emails. I don't even want to think of the problems that would lead me to.

* These aren't spam emails, and Gmail is pretty good at flagging them.

* My email cannot be deliberately mistyped. The person whose bank emails I received has 6 more characters than my personal email. 

* Is it a deliberate attempt/consipiracy by some group of people or hackers?

I'm not sure.

If you're a computer/cyber security expert reading this, can you suggest any steps I could take to prevent this "spam"?

Shall I use a new email service with a custom domain? Any cheap ones that you might want to recommend? 

If you're a normal person reading this -- you might want to check if the bank (and other) services you use have the correct email configured. 

We, as internet citizens, must also ask for laws redressing these types of lapses by the companies. Non-EU people who do not have the luxury of GDPR must demand similar laws of their governments. Services that you use must have the provision of deleting your account at the very least.

Follow more of this discussion on [HackerNews](https://news.ycombinator.com/item?id=29749715).
