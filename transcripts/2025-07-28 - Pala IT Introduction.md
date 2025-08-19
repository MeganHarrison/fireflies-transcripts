# Pala IT Introduction
**Meeting ID**: 01K18WF1NDTKQ8SM4T87ASZGKK
**Date**: 2025-07-28
**Duration**: 28.450000762939453 minutes
**Transcript**: [View Transcript](https://app.fireflies.ai/view/01K18WF1NDTKQ8SM4T87ASZGKK)
**Participants**: mcalcetero@alleatogroup.com, efortuna@palait.com

## Transcript
**Mcalcetero**: Example note to self or bonuses or salary and we're trying to figure out who is IT creating it.
**Mcalcetero**: So we send the IP addresses to Microsoft and they're saying it's from Japan, they're saying it's from Canada.
**Mcalcetero**: So we don't know exactly what's going on.
**Mcalcetero**: And they told me that part of it is just that we don't have our DNS records in the email.
**Mcalcetero**: So what we had to do is just to set them up from the website.
**Mcalcetero**: So that's what I reached out to Shelby telling her that we need to do it from the website, but then she said it's from the email and then she suggested you as an IT person that can help us with that.
**Mcalcetero**: So I don't know.
**Mcalcetero**: That's the context, that's the issue.
**Mcalcetero**: We are not completely sure like our host if it's bluehost or you know, the people that Shelby work with.
**Mcalcetero**: But other than that is just as a matter of helping, you know, our email to get, to get better traction and everything and to be like secure.
**Mcalcetero**: Especially for Brandon, which is a person who is receiving these emails.
**Efortuna**: Okay, yep.
**Efortuna**: So Brandon and Brandon, not confusing at all.
**Efortuna**: So, okay, so which, you know, I guess, you know, first Lane, I guess we'll kind of hold, backtrack just a little bit and I'll tell you a little bit about us and then we can try to, you know, go into the deeper conversations as to, you know, what actually is affecting it, where it's coming from.
**Efortuna**: So obviously we're a cybersecurity company.
**Efortuna**: We're a managed services company that obviously takes care of companies such as yourselves.
**Efortuna**: It needs, whether it be from a hosted platform, just a basic check in or a full blown organizational structure.
**Efortuna**: Myself, I end up acting as a virtual CIO for majority of the companies that we end up partnering with, but those are the ones that have 50 plus end users users with us at that particular time.
**Efortuna**: Majority of our small business clients are about 10 users at the very minimum for their parts with us.
**Efortuna**: But we take care of all of their check ins, all of their devices, as well as ensuring that the security aspect for setup configurations are all done.
**Efortuna**: And then of course we can go into deeper side of things from the DNS management, which is what you're needing currently is the DNS management side of stuff for email.
**Efortuna**: And then that's, you know, the gist of it for us now with yours, you know, I noticed that you are using Microsoft 365 for, you know, your email collaborations, you know, and then, you know, from there, you know, obviously I can tell, you know, the DMARC, DKIMs and stuff aren't set up currently.
**Efortuna**: So who do you use for your, like your domain registrar?
**Efortuna**: You said bluehost earlier.
**Mcalcetero**: So.
**Mcalcetero**: So we thought it was Microsoft, but I think they kind of like dig it in and they told me, no, it's actually bluehost.
**Mcalcetero**: So I don't recognize like anybody I've been in touch with from bluehost.
**Mcalcetero**: So that's what I wanted to confirm with Shelby because they were the people who start building the website for us.
**Mcalcetero**: So I have no idea.
**Efortuna**: Okay.
**Efortuna**: Because I saw like Wild Wild west or something earlier as far as who registered the domain for y' all or that may have been.
**Efortuna**: I've looked up a few companies this morning.
**Efortuna**: So it's.
**Efortuna**: Let me go back and I'll double check and I can tell you here in just a second.
**Mcalcetero**: Is.
**Efortuna**: And yeah, it was Wild West Domains.
**Efortuna**: Okay, so Wild West Domains is the site that.
**Efortuna**: Where the domain is registered.
**Efortuna**: I do see the Microsoft online.com as your name servers.
**Efortuna**: So when you.
**Efortuna**: When you all signed up for 365, how did y' all do it exactly?
**Mcalcetero**: You mean like, how did we start with them?
**Mcalcetero**: Yeah, so I have no.
**Mcalcetero**: I mean, so the thing is that we just, I think random purchase, probably like a licensing from Microsoft.
**Mcalcetero**: And as administrator, that's what we've been doing, like managing everything as administrator, setting down licenses with Alito Group.com, which is our domain, and then that's it.
**Mcalcetero**: But that's the only thing we have done, to be honest.
**Mcalcetero**: So that's why the Microsoft people were telling me, no, you need to do more verification on it because you didn't have the DNS records and the dmarc.
**Mcalcetero**: And I was like, okay, so that's what he said.
**Mcalcetero**: Try to contact the website people.
**Mcalcetero**: But now she'll be getting suggested you.
**Mcalcetero**: So.
**Mcalcetero**: But honestly, I don't.
**Mcalcetero**: The only thing I think is just we purchase a license with them, like a company license, and that's it.
**Efortuna**: Okay.
**Efortuna**: And then for your.
**Efortuna**: With the domain itself, do you all have access to be able to add in DNS records?
**Mcalcetero**: I have no.
**Mcalcetero**: I don't think so.
**Mcalcetero**: I have no idea.
**Mcalcetero**: So because when I was with Microsoft, I told them, how do we do that?
**Mcalcetero**: And they said, no, you cannot do it.
**Mcalcetero**: They have to do it from the domain, from the website.
**Mcalcetero**: And I was like, okay, so let me talk to them.
**Mcalcetero**: And the only person I know from the website is Shelby.
**Mcalcetero**: So that's what I actually asked her, if Bluehost is our actual host.
**Mcalcetero**: And because the Microsoft.
**Mcalcetero**: Microsoft keep telling me it has to be from the website and I'm like.
**Efortuna**: Okay, so Bluehost, do you all have access or a cPanel access to Bluehost at all?
**Mcalcetero**: No.
**Efortuna**: Okay.
**Mcalcetero**: Yeah.
**Efortuna**: All right then.
**Efortuna**: Well, that will be where we definitely have to start at.
**Efortuna**: So your admin panels with Microsoft and stuff.
**Efortuna**: Do you all have access to the admin panel at all?
**Efortuna**: Okay.
**Mcalcetero**: For Microsoft.
**Mcalcetero**: For Microsoft.
**Mcalcetero**: So we have the admin center and that's what we've been doing.
**Mcalcetero**: Like everything.
**Mcalcetero**: So I can show you what we have so far, but other than that.
**Efortuna**: Sure, that'd be a good one.
**Mcalcetero**: So let me just go ahead and.
**Mcalcetero**: Yes, let me just go ahead and do this.
**Mcalcetero**: So let me go ahead and share my screen with you.
**Mcalcetero**: You can see my screen.
**Mcalcetero**: And let me just go here and let's do.
**Mcalcetero**: So I have the.
**Mcalcetero**: Everything is here.
**Mcalcetero**: So this is what we have from the Microsoft 361 second snowing.
**Mcalcetero**: This is slow.
**Efortuna**: Yeah.
**Efortuna**: The Ackerman center is obnoxiously slow these days.
**Mcalcetero**: Yeah.
**Mcalcetero**: Is not that slow.
**Mcalcetero**: I mean, it is slow, but not that.
**Mcalcetero**: Okay, there you go.
**Mcalcetero**: Apologize with the noise.
**Mcalcetero**: My daughter is just here.
**Efortuna**: How old is she now?
**Mcalcetero**: She's gonna be eight months in a week.
**Mcalcetero**: So she's having.
**Mcalcetero**: She's eating her fruit.
**Mcalcetero**: So.
**Efortuna**: Sorry, I just turned.
**Efortuna**: I got twin girls, so.
**Efortuna**: Yeah, I understand.
**Efortuna**: Mine just turned 11, so yeah.
**Mcalcetero**: Beautiful.
**Mcalcetero**: Nice.
**Mcalcetero**: Okay, so this is what we have.
**Efortuna**: Okay.
**Mcalcetero**: And okay, so usually, for example, when I show them.
**Mcalcetero**: Let's say we're going to set up a new email or something.
**Mcalcetero**: So this is our domain.
**Mcalcetero**: So our domains is this one.
**Mcalcetero**: It's a little group dot com.
**Efortuna**: Right.
**Mcalcetero**: And we are paying for each.
**Mcalcetero**: You know.
**Efortuna**: Right.
**Efortuna**: So your.
**Efortuna**: Your domain itself.
**Efortuna**: Word of Joo.
**Efortuna**: Procure that domain.
**Mcalcetero**: Second question, I think it was.
**Mcalcetero**: We thought it was from Microsoft because actually.
**Mcalcetero**: So if I want to go to that one, should I close this?
**Mcalcetero**: So that's a good question.
**Mcalcetero**: I mean I have all the Microsoft.
**Efortuna**: That's the interesting part is like, you know, it shows Microsoft online as your DNS server, which is odd.
**Efortuna**: I mean I've.
**Efortuna**: I've never seen that.
**Mcalcetero**: When I try to turn on the DNS because I do have something for the DNS records I'm showing you here because I save.
**Efortuna**: It here because usually that'll be on Azure side.
**Mcalcetero**: Yeah.
**Mcalcetero**: Here if I go to the security Microsoft and there is a section that it says turn on your DNS and when they try to, there's an error.
**Mcalcetero**: I'LL show you here.
**Mcalcetero**: So email authentication settings.
**Mcalcetero**: Right.
**Mcalcetero**: So I'll either.
**Mcalcetero**: And then if I go to.
**Mcalcetero**: Exactly.
**Efortuna**: Yeah.
**Efortuna**: And then that wouldn't be the DNS, you know, side of things that those are the DKIM records that it's looking to get set up.
**Mcalcetero**: Yes.
**Mcalcetero**: And then if I.
**Mcalcetero**: So the person told me you click here and then if you want all the dk, you're right.
**Efortuna**: Then at the bottom there, it's where it has the actual record names.
**Efortuna**: You know, that's what you know, the selector one, you know and the selector two both have to be created on the DNS server.
**Efortuna**: And now just trying to figure out, you know where your DNS server is.
**Mcalcetero**: Yeah, it's host name, host name to selector to domain key aldito.
**Mcalcetero**: But yeah, it's just rotating keys.
**Mcalcetero**: Yeah, that's a good question.
**Mcalcetero**: So that's what we're trying to verify our DNS.
**Mcalcetero**: Where are they located?
**Mcalcetero**: And I thought so the.
**Efortuna**: So it's three.
**Efortuna**: It is Office 365 as part of the Microsoft Online domains.
**Efortuna**: Okay, so let's in the top there actually go ahead and exit out of that real quick.
**Efortuna**: And then let's go over on the left hand side.
**Efortuna**: Let's go back over to the.
**Efortuna**: Yeah, the portal and then let's scroll down where it says all admin centers on the left hand side there and.
**Mcalcetero**: Then.
**Efortuna**: Change Preview search.
**Efortuna**: Keep scrolling down.
**Mcalcetero**: That's it.
**Mcalcetero**: Those are the only ones we have only until Viva Engage.
**Mcalcetero**: Yes.
**Efortuna**: Okay.
**Efortuna**: On the, where it says Identity on the left hand side, click on the Identity section.
**Efortuna**: Let's go in there.
**Efortuna**: Then on the bottom where it says Domain Services on the left hand side.
**Efortuna**: Right.
**Efortuna**: And then.
**Efortuna**: Well that doesn't help.
**Mcalcetero**: Anything.
**Efortuna**: Yeah, you just have to like.
**Efortuna**: Because there should be some DNS option.
**Efortuna**: There's.
**Efortuna**: There's DNS records within entrepreneurs but your subscription isn't actually started with it.
**Efortuna**: So let's look it up some other information online to see where if anyone has a secret path to get into it.
**Efortuna**: All right, so let's in the, let's go back over to the admin portal and then let's go into.
**Efortuna**: Scroll up on the left hand side, go into Settings and then Domains and then let's click on your domain and then DNS records.
**Efortuna**: Okay.
**Efortuna**: All right, here we go.
**Efortuna**: This is, this is where we would actually manage things.
**Mcalcetero**: Okay.
**Efortuna**: Okay.
**Efortuna**: So I guess a couple things I guess before we, you know, dive in deep into this year.
**Mcalcetero**: Yes.
**Efortuna**: Your company, do you currently have IT support at all?
**Mcalcetero**: We don't and that's what I wanted to talk to you about this.
**Mcalcetero**: You know, like if we can have a 90 person doing that or.
**Mcalcetero**: Actually, because I think.
**Mcalcetero**: And most of the things actually is that a lot of of our employees are receiving a spam emails and I think it's actually because we're not having like the maintenance the proper things.
**Mcalcetero**: So I think it'll be good to have, you know.
**Mcalcetero**: And I already talked to Brandon about this.
**Mcalcetero**: I told him I do want to.
**Efortuna**: Oh, sorry, froze up there.
**Efortuna**: Yeah.
**Mcalcetero**: Can you hear me?
**Efortuna**: Yeah, again.
**Mcalcetero**: It says do not disturb for some reasons.
**Mcalcetero**: Anyway.
**Efortuna**: Yeah, okay.
**Efortuna**: I can dropped off for a second there.
**Mcalcetero**: Yes.
**Efortuna**: Okay, so all right.
**Efortuna**: How many end users do you.
**Efortuna**: You currently have within your.
**Mcalcetero**: So right now we have 13.
**Mcalcetero**: 13 people, but it's gonna keep growing.
**Efortuna**: Okay, perfect.
**Efortuna**: Okay, good.
**Efortuna**: I just want to make sure like you were over that 10 mark, you know, is kind of the key there, you know, because, you know, our.
**Efortuna**: We have different tier packages, you know, internally as far as, you know, what they do and you know, don't offer, you know, from the basic level all the way up to the complete level.
**Efortuna**: You know, the basic side starts out like $40 an end user and then goes up to 85 an end user for the complete per month.
**Efortuna**: But all of them include a large number of different packages that one go into support rather than just basic monitoring and being proactive versus reactive.
**Efortuna**: Getting into the complete side of things where we look to one, ensure that you do have the security levels that are met.
**Efortuna**: You have your spam protection, you do have security awareness trainings that go into effect that all companies have to have cybersecurity policies these days.
**Efortuna**: So having that part is a necessity.
**Efortuna**: And then we can look to ensure compliance side of stuff is always set up.
**Efortuna**: And then, you know, there's the.
**Efortuna**: The base side of things where, you know, discounts come into play when support is needed.
**Efortuna**: I would definitely like to, you know, get a package out to y'.
**Mcalcetero**: All.
**Mcalcetero**: Yes please.
**Efortuna**: And then that way we can kind of go over more, you know, what's needed, you know, but for now, if.
**Mcalcetero**: You can start from the basic package to the.
**Mcalcetero**: So that'll be awesome.
**Mcalcetero**: So we can, if you have like, you know, items or something will be great.
**Mcalcetero**: So.
**Mcalcetero**: And actually this will be one of the things that I can tell to Brandon, like he can help us with these things with the email and DNS.
**Mcalcetero**: So if you can obviously help us with that, then that.
**Mcalcetero**: That'll be even easier, you know, to have an IT because we don't have it and it's important to have.
**Efortuna**: Yes.
**Efortuna**: Yeah, definitely.
**Efortuna**: That way, the proactive side of stuff from, you know, the maintenance, monitoring, you know, something that if each individual user is just doing their own thing, you know, there's no telling how many updates, you know, could potentially be missing.
**Efortuna**: You know, then of course, security vulnerabilities, you know, we cover your antivirus costs as well.
**Efortuna**: So, you know, those type of coverages are automatically included within the services.
**Mcalcetero**: Okay.
**Efortuna**: So you don't have to worry about, you know, going out procuring any additional, you know, licenses or, you know, other people tend to falling for your additional scams on licensing.
**Efortuna**: So for your admin center here, what I'd like to, you know, go ahead and do for you, at least get you rolling.
**Efortuna**: Um, and that way, you know, then I can obviously get the package and stuff sent out and everything later on.
**Efortuna**: But, you know, what I'd like to do is at least get you set up, you know, for, you know, your dkim and DMARC stuff, you know, that Shelby is needing for her side and what you're needing to be able to send out stuff properly.
**Efortuna**: If that works for you.
**Mcalcetero**: Yeah, that's perfect.
**Mcalcetero**: That's wonderful, Brandon.
**Mcalcetero**: I mean, that's great.
**Mcalcetero**: And I'm, I'm all for it, to be honest, and I'm going to convince Brandon to have it because it's really important to have it.
**Mcalcetero**: So.
**Mcalcetero**: Yeah.
**Efortuna**: Okay, that's good.
**Efortuna**: Well then let's go ahead and share back out your screen real quick.
**Mcalcetero**: I'm trying to.
**Mcalcetero**: Let me see if you can see because for some reason something happened with teams and he's acting weird.
**Mcalcetero**: So let me see why.
**Mcalcetero**: Can I go back to my.
**Mcalcetero**: Okay, here and then let me see if you can see my screen now.
**Mcalcetero**: Okay.
**Efortuna**: Yeah, perfect.
**Mcalcetero**: Okay, perfect.
**Mcalcetero**: Okay.
**Efortuna**: All right, so let's go back over to your other tab where the security side is.
**Efortuna**: Should be the email authentication tab.
**Efortuna**: The.
**Efortuna**: That's there in the far, far right.
**Mcalcetero**: This one.
**Mcalcetero**: This one.
**Efortuna**: Right, the next one over.
**Mcalcetero**: Oh, this one.
**Mcalcetero**: Yeah.
**Efortuna**: Yep, let's go to that one.
**Efortuna**: All right, so then let's go ahead and click on your domain.
**Mcalcetero**: Here.
**Efortuna**: Yep.
**Efortuna**: And then scroll down to where it says the host name, how it has the selector one.
**Efortuna**: What we're going to do is we're going to highlight the selector 1/ underscore domain key.
**Efortuna**: So let's word just as the host name side of it.
**Mcalcetero**: So from here, from domain key, so.
**Efortuna**: The host name, the one above it where it says host name.
**Efortuna**: You'll just want that top part.
**Efortuna**: Yeah, that top Part first let's copy that and then let's go back over to domain side.
**Mcalcetero**: Okay.
**Efortuna**: And then click on Add Record in the top left corner.
**Mcalcetero**: Add record.
**Mcalcetero**: Yep.
**Efortuna**: And then change the type to C name to cname and then paste the host name there.
**Efortuna**: And then let's go back over to that tab, the email authentication tab.
**Efortuna**: And then now copy the points to address, which will be the selector one, all the way down to the Microsoft here.
**Efortuna**: Correct.
**Efortuna**: Yep.
**Mcalcetero**: And then paste it here.
**Efortuna**: Yep, correct.
**Mcalcetero**: Okay.
**Efortuna**: And dot Microsoft.
**Efortuna**: All right, so yeah, we'll go with that.
**Efortuna**: Click Save.
**Efortuna**: And then let's go back to the email authentication side and then we'll do the same thing for the two.
**Efortuna**: So selector two.
**Efortuna**: And then just go back and you know, add record C name and put the host name and then go back over there and copy the bottom part and hit Save.
**Mcalcetero**: Okay.
**Efortuna**: And go back over to the email authentication side real quick.
**Efortuna**: And then click on copy.
**Efortuna**: That's there.
**Mcalcetero**: Okay.
**Efortuna**: Then open up Notepad.
**Efortuna**: Yeah, either Notepad or Notepad, whichever.
**Efortuna**: And then paste it there.
**Efortuna**: Okay, cool.
**Efortuna**: I just want to make sure it was Microsoft and not they weren't missing the.com on there.
**Efortuna**: So.
**Efortuna**: Okay, cool.
**Efortuna**: You close that out.
**Efortuna**: All right, so you should be good to close that and go back over to.
**Efortuna**: Yep.
**Efortuna**: Your email authentication.
**Efortuna**: Yep, correct.
**Efortuna**: And then go ahead and just close that.
**Efortuna**: Or actually right there in the top, go ahead and mark it over to enabled.
**Mcalcetero**: Yeah, let's see.
**Mcalcetero**: Okay.
**Efortuna**: All right, so that part's done.
**Efortuna**: So now we need to add in my.
**Mcalcetero**: Takes a minute to synchronize with the change.
**Mcalcetero**: So.
**Mcalcetero**: Okay.
**Efortuna**: Right.
**Efortuna**: So now we need to add in the DMARC side of things.
**Efortuna**: So that's dmarc.
**Efortuna**: And you know, the other side of things are obviously other things that we can help maintain a monitor for you as well.
**Efortuna**: We provide a service that will monitor, ensure that things are actually flowing through.
**Efortuna**: Let me get on my service real quick.
**Mcalcetero**: Thank you for this.
**Mcalcetero**: Seriously.
**Mcalcetero**: I didn't knew it was going to be that easy just to add on record.
**Mcalcetero**: And that's it.
**Mcalcetero**: Because Microsoft didn't figure it out.
**Mcalcetero**: They were like, no, they have to.
**Mcalcetero**: Okay.
**Efortuna**: It's interesting that, you know, since they're the ones actually providing your DNS service, you know.
**Mcalcetero**: Yes.
**Efortuna**: They should have been able to, you know, give you better instructions and I'm.
**Mcalcetero**: Gonna let them know.
**Efortuna**: So.
**Efortuna**: All right, so okay, so in your go back, you can close.
**Efortuna**: Hit the X there and go back over to Domains.
**Efortuna**: Real quick.
**Mcalcetero**: Domains.
**Efortuna**: Yep.
**Efortuna**: And then click on Add Record.
**Mcalcetero**: Okay.
**Efortuna**: And then you'll want to do.
**Efortuna**: You know, it'll be a text record.
**Efortuna**: So in the text or your name, you'll do under the underscore.
**Efortuna**: And then, you know, dmarc, D mark.
**Efortuna**: And then just, just like that.
**Efortuna**: And then in the text value, if you go back to that email chain with Shelby in it.
**Mcalcetero**: Email, which Shelby.
**Mcalcetero**: Correct?
**Efortuna**: Yes.
**Efortuna**: Even mine.
**Efortuna**: Yep.
**Efortuna**: And then square there, actually.
**Efortuna**: So where it says the.
**Efortuna**: The value shows the D mark.
**Efortuna**: Copy that.
**Efortuna**: You know, all the way over to just the none.
**Efortuna**: You know, that's where the semicolon is with none.
**Mcalcetero**: The sim here.
**Efortuna**: Yeah.
**Efortuna**: So where it says the.
**Efortuna**: The v equals d mark 1 and then it's, you know, semicolon.
**Mcalcetero**: Oh, here, sorry.
**Mcalcetero**: Until none here.
**Efortuna**: Yeah, copy that part, Copy that.
**Efortuna**: Then go paste that into the value.
**Mcalcetero**: Okay.
**Efortuna**: That way we're just getting the default one kind of set up, but we'll obviously having none there doesn't, you know, help, you know, much.
**Efortuna**: You know, it just shows that it's there.
**Mcalcetero**: Okay.
**Efortuna**: But this will be where it's a starting point, at least to turn it on.
**Efortuna**: And then after, obviously, we get to our services, kind of get in play, we can actually get it corrected to make it to where it'll be rejected or quarantined and actually have those messages sent over to our admin portal and stuff properly.
**Efortuna**: So you should be able to click save.
**Mcalcetero**: Okay.
**Efortuna**: And then now you go over and look at your domain again.
**Mcalcetero**: Here, click on my domain where.
**Efortuna**: No, I'm looking on this side right now.
**Mcalcetero**: Oh, sorry.
**Efortuna**: That's okay.
**Efortuna**: It's.
**Efortuna**: The policy just got enabled, so I'm waiting on it to actually take effect here.
**Efortuna**: All right, so, yeah, I do see, it's.
**Efortuna**: All right, so it is published now.
**Efortuna**: And then DKIM's there, so obviously just not being enabled is the, the key thing there.
**Efortuna**: So go and click on the.
**Efortuna**: The checkbox next to the.
**Efortuna**: The TXC words for the dmarc.
**Mcalcetero**: Okay.
**Efortuna**: And then just going to.
**Efortuna**: Or look at the three dots and see if it'll allow you to hit edit.
**Efortuna**: There you go.
**Efortuna**: Edit record and then change the none to put quarantine in there instead of none.
**Mcalcetero**: Quarantine?
**Efortuna**: Yes.
**Mcalcetero**: Like this?
**Efortuna**: Yes, just like that.
**Efortuna**: And click save.
**Mcalcetero**: Okay.
**Efortuna**: Now let me refresh on this side.
**Efortuna**: And there we go.
**Efortuna**: Now it's enabled.
**Efortuna**: Okay, so now we actually have it to where it's.
**Efortuna**: It's.
**Efortuna**: It's not going to send any forensic information to an admin or anything, but it is turned on at least now to where it says that anything that doesn't pass your DMARC records itself or your SPF itself will automatically say, hey, you need to quarantine this message.
**Efortuna**: It's not a guarantee, but it makes it to where your domain is not spoofable anymore at least.
**Mcalcetero**: Thank you so much.
**Mcalcetero**: Let me know actually if I owe you something for this because this was a lot, to be honest.
**Mcalcetero**: It wasn't just for you just.
**Mcalcetero**: No, you actually taught me a lot.
**Mcalcetero**: So if you actually want, you know, like an invoice or something for this, please let me know so I can send it to you.
**Mcalcetero**: And then also please don't forget the packages because I do want to have it for our company.
**Mcalcetero**: Okay.
**Efortuna**: Yep, definitely.
**Efortuna**: We'll get those out later on this afternoon and then waiting on my, you know, my, my sales guy to get back in the office and then.
**Mcalcetero**: Awesome.
**Efortuna**: Once he's back on site and then we'll be able to get those together for you and then get it shot over and hopefully we'll be able to discuss further.
**Mcalcetero**: Yes, please.
**Mcalcetero**: And then this is it, right?
**Mcalcetero**: I don't need to do anything else according to what they told me.
**Mcalcetero**: So I think that's it.
**Efortuna**: Yeah.
**Efortuna**: As far as email goes, like I said, your DKIM's active and your DMARC's act now.
**Efortuna**: It, like I said, it could take anywhere from an hour to 48 hours just from propagation time.
**Efortuna**: So definitely give it the day for other servers to actually see it and recognize it.
**Mcalcetero**: Okay.
**Efortuna**: But yes, it will enable, you know, messages to not be automatically declined.
**Efortuna**: So like with the large.
**Efortuna**: I'm not sure if you actually have been over to our, our site at all or anything yet.
**Mcalcetero**: I think.
**Mcalcetero**: No, your side.
**Mcalcetero**: No, I haven't.
**Efortuna**: Yeah, let me.
**Efortuna**: I'll send you here.
**Mcalcetero**: I think I have your pala it correct.
**Mcalcetero**: Palit.com yeah, I have it here.
**Efortuna**: Yeah, I'll pop it up in chat real quick here.
**Efortuna**: But I built out a page that's on here to actually go through and help educate others in general as far as the restrictions and authentication and why those are the things that we've actually just completed today in a way.
**Efortuna**: But the large vendors, especially Microsoft, Gmail, they all block domains now that don't follow these best practices, of course.
**Efortuna**: So which obviously that's, you know, what you were running into.
**Efortuna**: So now that you're in compliance, you know, those messages will actually be able to, you know, one get through and won't start going to junk mail for other, you know, people as well as they, as they start seeing any domain gets warmed up towards, you know, shows as hey, we've got a positive reputation now, so we're good to go and they just pass us through, so.
**Mcalcetero**: Awesome.
**Efortuna**: Cool.
**Efortuna**: All right.
**Mcalcetero**: Okay.
**Mcalcetero**: Thank you so much for this.
**Mcalcetero**: Yes, please send me everything, Brandon, and thank you again for your help.
**Mcalcetero**: I'm really, really looking forward to work with you because we do need it.
**Mcalcetero**: And I'm going to convince Brandon also, so I'll let him know.
**Mcalcetero**: Thank you so much for your help.
**Mcalcetero**: I'll let Microsoft know and then, yeah, looking forward to talk to you and start working with you.
**Mcalcetero**: Okay.
**Efortuna**: Likewise.
**Efortuna**: It's a pleasure to meet you, of.
**Mcalcetero**: Course, my friend and YouTuber.