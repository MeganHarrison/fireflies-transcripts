# Alleato Group + AI Caleb
**Meeting ID**: 01JWKWA9YFSEZJSBVZJ1W6A7E9
**Date**: 2025-06-02
**Duration**: 29.700000762939453 minutes
**Transcript**: [View Transcript](https://app.fireflies.ai/view/01JWKWA9YFSEZJSBVZJ1W6A7E9)
**Participants**: bclymer@alleatogroup.com, calebbarnwell@gmail.com

## Transcript
**Bclymer**: Hey, Caleb, how are you?
**Calebbarnwell**: You hear me?
**Calebbarnwell**: Yep.
**Calebbarnwell**: How's your weekend, man?
**Bclymer**: Good, it's good.
**Bclymer**: How's yours?
**Calebbarnwell**: Oh, it was good as well.
**Calebbarnwell**: Just, you know, try to relax, take it easy.
**Calebbarnwell**: And you just got back from a trip yourself?
**Bclymer**: Yeah, yeah, I was in Cancun for the weekend.
**Calebbarnwell**: Oh, there you go.
**Calebbarnwell**: That's a good way to spend the time right there.
**Bclymer**: I know, right?
**Calebbarnwell**: Yeah.
**Bclymer**: Body disagrees.
**Calebbarnwell**: Yeah, yeah, yeah.
**Calebbarnwell**: I get a little bit of sun, huh, out there.
**Calebbarnwell**: Well, this should be hopefully, you know, pretty.
**Calebbarnwell**: Pretty short and sweet, but I wanted to kind of just get you an update on the things I've been looking through and then, you know, how we can kick this thing off if you're ready to go on it.
**Calebbarnwell**: And so let me, let me see here.
**Calebbarnwell**: I can get this screen shared.
**Calebbarnwell**: Let's do.
**Calebbarnwell**: I'm on Mac here, so I just have to allow it in my system preferences to share the screen.
**Calebbarnwell**: That's crazy.
**Calebbarnwell**: Okay, let me.
**Calebbarnwell**: Let me just share a link to the document.
**Calebbarnwell**: It says I've got to restart the browser to actually share the screen.
**Calebbarnwell**: Sorry about that.
**Calebbarnwell**: Okay.
**Calebbarnwell**: Okay.
**Calebbarnwell**: I just put it in the chat.
**Calebbarnwell**: So that document there should let you open that up.
**Calebbarnwell**: And that's pretty much just the scoping I wanted to walk you through.
**Calebbarnwell**: And then I'm going to put one more link in the chat that we can go after that too.
**Calebbarnwell**: That's just going to be.
**Calebbarnwell**: I wanted to walk you through just the initial kind of agreement we can do to get the thing kicked off.
**Calebbarnwell**: So those would be the two documents anyway.
**Calebbarnwell**: On the first one, just put kind of on the top, the general, you know, outline of what are we building and what we had talked about.
**Calebbarnwell**: And that's again, just a tool that acts as a task aggregation.
**Calebbarnwell**: We're targeting primarily notion.
**Calebbarnwell**: We had talked about Job Planner as well.
**Calebbarnwell**: I think for this initial phase, what the game plan is going to have to be is a notion.
**Calebbarnwell**: We can access the API.
**Calebbarnwell**: We should be able to get all that information, no problem.
**Calebbarnwell**: When it comes to Job Planner, I have not found any sort of API that we can use.
**Calebbarnwell**: There is some of the data that we can export and there could be a potential for scraping down the line.
**Calebbarnwell**: But just to get this thing into a minimum viable product, to get phase one kind of out of the way, we're gonna.
**Calebbarnwell**: What.
**Calebbarnwell**: What my plan is is to have an optional job plan or data upload, as you'll see down below.
**Calebbarnwell**: So to get started, we're gonna.
**Calebbarnwell**: We're gonna pull what we can from Notions API and then Also hook up to a storage unit where we can export Job Planner data and just throw it in there and that's how we can sort of connect to it.
**Calebbarnwell**: But if we want to do anything extended beyond that, I think we're gonna have to, you know, look further into other options.
**Calebbarnwell**: Job Planner, that was the only thing that I came across for that.
**Bclymer**: So Job Planner has an open API.
**Calebbarnwell**: They do as well.
**Calebbarnwell**: Okay, yeah.
**Calebbarnwell**: If you will.
**Calebbarnwell**: You send me the link to that if you've got that.
**Calebbarnwell**: I did not see anything when I looked up Job Planner Construction API.
**Calebbarnwell**: If they have an API, we should be able to also include that in our data aggregation phase.
**Bclymer**: Yeah, I.
**Calebbarnwell**: And you don't have to right now, Brandon, but let's stay in touch about that.
**Calebbarnwell**: And if we can find access to the API, that should be no problem to include.
**Bclymer**: Yeah, I mean, I just googled it.
**Bclymer**: It said it does.
**Calebbarnwell**: With its robust API API access.
**Calebbarnwell**: Okay, okay.
**Calebbarnwell**: I'm not, I don't.
**Calebbarnwell**: I'm not too worried about how that's going to factor into the overall scope and in pricing or anything like that for you, Brandon.
**Calebbarnwell**: So if we can get access to that API, I don't imagine that's going to be too much extra complication for this.
**Calebbarnwell**: So we'll stay in touch on that and then see if we can get access to that and then throw that in if so.
**Calebbarnwell**: If not, we'll have to kind of come up with a separate game plan and target Notion, but definitely wanted to update you there.
**Calebbarnwell**: But beyond that, the scope is to also send out the automated summaries to get this thing started again with just the first steps, I think emails.
**Calebbarnwell**: I know you talked about doing Outlook in teams and we can definitely get to that point, but I think just sending out an email to your team daily and weekly would be the place to start.
**Calebbarnwell**: So we make sure that's working properly, then integrate it to other tools from there.
**Calebbarnwell**: So, and then just you have on.
**Bclymer**: Here build web application backend.
**Bclymer**: What does that mean exactly?
**Calebbarnwell**: Well, we need.
**Calebbarnwell**: We need a backend server that runs this tool so that.
**Calebbarnwell**: That is the tool itself.
**Calebbarnwell**: We need something that's going to ping the Notion API and that's going to process and send, gather all the information and data and send it to our generative AI source.
**Calebbarnwell**: So that.
**Calebbarnwell**: That is the backend for the tool tool itself.
**Calebbarnwell**: And that's where our logic is going to be running.
**Calebbarnwell**: So you can sort of think about the connector between Notion and Chat GPT or whatever Generative AI.
**Calebbarnwell**: We end up going for that back End server is the middleman for that.
**Bclymer**: Let me try to understand this.
**Bclymer**: Yeah, so yeah, we have a website.
**Bclymer**: Is that not on a server?
**Calebbarnwell**: That is on a server, but your website is, let me see here.
**Calebbarnwell**: Your website is likely a front end.
**Calebbarnwell**: Well, let me pull up your website now.
**Calebbarnwell**: But this will be a separate tool beyond what your website actually performs.
**Calebbarnwell**: So let's see here.
**Calebbarnwell**: What are you hosting your website through right now, Brandon?
**Bclymer**: What do you mean hosting it through?
**Bclymer**: Like godaddy?
**Calebbarnwell**: Yeah, well that's, that's the domain where you'll get the Aletto group.com domain and they, they, they do actually have some website building and hosting services but we're just.
**Calebbarnwell**: Wherever you build this website through.
**Bclymer**: Is that nothing?
**Bclymer**: Go ahead.
**Calebbarnwell**: Oh, do you know how, how this website was built?
**Calebbarnwell**: Was it custom or was it squarespace or something like that?
**Bclymer**: No, it's custom.
**Calebbarnwell**: It's custom.
**Calebbarnwell**: Okay.
**Calebbarnwell**: If it's custom, I mean we can potentially tie into whatever web servers you're using right now.
**Calebbarnwell**: But whatever functionality this tool we're going to build, it's going to be separate than your website.
**Calebbarnwell**: Looking at it now, unless you have like an actual web application within this, this is more of a front facing sales base, you know, contact information, you know, featured projects, sort of just people can come here and get an idea of what you do.
**Bclymer**: What do you mean?
**Bclymer**: What'd you say?
**Bclymer**: Application application in it?
**Bclymer**: What do you mean?
**Calebbarnwell**: So basically the, the tool that we're building is going to be a generative AI project management middleman that pulls the notion data, throws it into a generative AI, sends out the automated summaries.
**Calebbarnwell**: That's not something that your website allows for.
**Calebbarnwell**: Right now there's a potential that we could tie it into that.
**Calebbarnwell**: But when I say web application it's just, it's just a different, a separate tool from your website that is connected on the, on the Internet so that your team can interact with it and they maybe there's a separate login we can just.
**Bclymer**: So like, so you're saying it's, it's, it's essentially like a chat GPT website where I go in and type.
**Calebbarnwell**: Exactly, exactly, exactly.
**Calebbarnwell**: So that we'll start by built just building the back end for that and then later on on the that document you'll see I've got general outline of steps.
**Calebbarnwell**: Build web application back end, pull and aggregate notion data and then the optional job planner data.
**Calebbarnwell**: Import that data into generative AI, send out automated summary emails and then we get to the point of build web application front end.
**Calebbarnwell**: So a Lot of this stuff is all in the back end and we just need a place for that back end code to live and be interacted with.
**Calebbarnwell**: So that's all the back end is.
**Calebbarnwell**: It's just taking care of all this data, movement and all that.
**Calebbarnwell**: The front end is that last step and that's what would actually allow your team to interact with the tool, to submit the prompts and the questions that you have.
**Calebbarnwell**: And we could tie that into your existing website, but you would need to add some sort of login because I'm assuming we don't want just anybody to be able to use this.
**Calebbarnwell**: It's only an internal tool.
**Calebbarnwell**: So it's probably easiest that we go ahead and just make this a separate thing.
**Calebbarnwell**: We can tie it to your domain.
**Calebbarnwell**: It could be like AI.eletogroup.com and then only your internal team is able to access that or something like that.
**Calebbarnwell**: But so we can kind of talk about the specifics of that.
**Calebbarnwell**: But this, it is a separate thing from your website.
**Calebbarnwell**: The point of your website, it seems like to me right now, is so third parties can come and view what you guys do, who you are, so on, so forth.
**Calebbarnwell**: The point of this tool is for your internal team to be able to look at project management, ask it questions, send out automation on the emails front and stuff like that.
**Calebbarnwell**: So it's an internal tool versus an external tool, but they're both web applications at the end of the day.
**Calebbarnwell**: If that kind of breaks it down for you, Brandon.
**Bclymer**: Yeah, I think I understand.
**Calebbarnwell**: Yeah, absolutely.
**Calebbarnwell**: And then, yeah, so that, that's kind of the outline of the steps of how we'll do this thing, the expected expenses I put on there.
**Calebbarnwell**: Just so you have an idea of what this looks like, on a month to month basis, there's going to be the web app posting the backend that we just talked about, some sort of front end that, that your team can, can interact with, load up the web page, input the prompt, ask a question like what we talked about up there, what's still open on the Westfield project?
**Calebbarnwell**: Are there an any overdue tasks assigned to Jesse, so on, so forth.
**Calebbarnwell**: That's that front end is how they're going to be able to input those prompts and that's going to the back end.
**Bclymer**: So okay, so I guess my thought is like, with this AI, like can it, is it learning?
**Bclymer**: Right?
**Bclymer**: So for instance, like uploading minutes and stuff from meetings and can it learn or how does that work?
**Calebbarnwell**: Yes, yes.
**Calebbarnwell**: And that's where also on that document you'll see data storage we're going to have a middleman for some of the data.
**Calebbarnwell**: So those meeting minutes and stuff like that, I think what we can do is just sort of create a, an upload system through the front end where you can add data to the system itself and it can that that data that you're going to input is how it's going to learn those meeting minutes that you upload.
**Calebbarnwell**: Anything that goes into Notion, we can pull from the API.
**Calebbarnwell**: And also with the Job Planner, if we get the API hooked up, that's great.
**Calebbarnwell**: If not, you can still export a lot of stuff from Job Planner.
**Calebbarnwell**: So we can basically just have an open system that allows you to upload files as you go.
**Calebbarnwell**: Maybe you can upload some of the Firefly stuff.
**Calebbarnwell**: Whatever data you've got, we can upload in there.
**Calebbarnwell**: And then the AI is going to be hooked up to that data.
**Bclymer**: Let's say we have all of our Fireflies notes, every single meeting is recorded.
**Bclymer**: So I guess in reality my thought is that every meeting have his transcript.
**Bclymer**: So you could take that and input it in.
**Bclymer**: The AI knows, hey, you could ask a question about blah, blah, blah, job.
**Bclymer**: And it knows because every meeting has been uploaded for that.
**Calebbarnwell**: Absolutely.
**Calebbarnwell**: That's where this can go.
**Calebbarnwell**: We can build in an actual integration that is for you that says, hey, put all Firefly data in this Google Drive folder or something like that, wherever you store it on your site, and then we can directly integrate that to that data.
**Calebbarnwell**: That's kind of a step beyond, I think, this first phase of building this out.
**Calebbarnwell**: But I think that that's very easily something we can build towards after this, this initial phase.
**Calebbarnwell**: Because what I want to do for you here, Brandon, is just kind of get this project kicked off, get this tool started, hit on all these initial points we're talking about with Notion, with Job Planner.
**Calebbarnwell**: If we get to the API with allowing your team to interact with the chatbot and also train on any data that you can upload to a bucket.
**Calebbarnwell**: And I think from my standpoint, that's a really good starting place from a technical standpoint.
**Calebbarnwell**: And I know that there may be extra extensibility that you're going to want in the end, Brandon, but I think that's all stuff that we can build on top of.
**Calebbarnwell**: And so if we can kind of agree that, hey, this is a good place to start and this is a good scope, my thought is that, that we can essentially target a six week timeline and if you go to the other document, the service agreement, it's pretty basic bare bones service Agreement.
**Calebbarnwell**: But my thought would be that I think $5,000 is a really good price to get this thing started with.
**Calebbarnwell**: That's just from my side of kind of like, you know, and I don't want to go back and forth like in terms of negotiation or anything.
**Calebbarnwell**: 5,000 is just the number for me.
**Calebbarnwell**: That's like basically what on my side makes sense for me to do and what would be the minimum of that.
**Calebbarnwell**: And so I want to give you the best deal possible from my side, Brandon.
**Calebbarnwell**: So for me that's $5,000 at a six week timeline pretty much.
**Calebbarnwell**: And then from there we can start to add things on top of that.
**Calebbarnwell**: We can directly tie into your Firefly integration.
**Calebbarnwell**: Maybe there's some, you know, use case that you come across as you develop this thing that you want to add into there.
**Calebbarnwell**: We can definitely extend and build on top of this.
**Bclymer**: So, so what would you do you do you build this in Python or what do you do build it in.
**Calebbarnwell**: It's going to be a couple of different languages, but Python is going to be the backend.
**Calebbarnwell**: So Flask is probably what I'll make use of.
**Calebbarnwell**: That's a Python backend that allows us to build an API or sorry, a REST API that's going to manage our back end for the front end.
**Calebbarnwell**: I'm kind of open to technologies on that, but Python's not really a great front end language.
**Calebbarnwell**: So I may use something like JavaScript or react for that.
**Calebbarnwell**: That's pretty standard, just front end framework and I can, I can get something together pretty quickly for that.
**Calebbarnwell**: But mostly Python because I think it's going to be Python to grab the data from Notion to send it over to Chat GPT to build the data storage and stuff like that.
**Calebbarnwell**: And then we'll host the data storage and we'll host this Python application on a back end web server.
**Calebbarnwell**: I prefer to use Digital Ocean.
**Calebbarnwell**: That's kind of the pricing that I'm working off of.
**Calebbarnwell**: It's.
**Calebbarnwell**: It's basically the same idea as aws, just a different company and that kind of better targeted for small businesses where AWS is your more enterprise solutions and stuff like that.
**Calebbarnwell**: But mostly Python.
**Calebbarnwell**: Mostly Python, exactly.
**Bclymer**: And yeah, so, so front end is what I view like when I go to ChatGPT and I see that that is the front end you're talking about.
**Calebbarnwell**: Yes, when you, yeah, when you're interacting with Chat GPT, I don't know what they built theirs in, but that's the front end you're interacting with and then it's taking whatever Prompt you input and it's sending it straight to their backend servers.
**Calebbarnwell**: And then again, I don't know what the backend servers are written in either.
**Calebbarnwell**: It could be like a C Sharp language, it could be Python, I'm not sure.
**Calebbarnwell**: But that's, it's the same, same structure that we're going to have.
**Calebbarnwell**: Your team has an internal front end that they go.
**Calebbarnwell**: And there's, there's a, you know, it's probably going to be bare bones to start with, Brandon.
**Calebbarnwell**: Just, you know, a text box for your input prompt, an upload button for your files that you want to add to the storage that it can learn off of, but that's our front end.
**Calebbarnwell**: And then that prompt that you type in and press send, that's going to be sent to your Python backend directly.
**Calebbarnwell**: And then that's going to take care of the data aggregation, the data processing.
**Calebbarnwell**: Send that back to the front end once it's got the response.
**Bclymer**: So once you build this stuff, then what if you get hit by a bus in a year from now, do we have access to be able to change it?
**Calebbarnwell**: Absolutely.
**Calebbarnwell**: Sorry, I should have walked you through on the service agreement.
**Calebbarnwell**: So to kind of highlight the important points of the service agreement, you'll see the project description, the scope of the services, and then the.
**Calebbarnwell**: And I'm going to send this over.
**Calebbarnwell**: This is just kind of the Google Docs version.
**Calebbarnwell**: I'll actually send over a version that we can sign along with the initial invoice.
**Calebbarnwell**: But payment terms, initial deposit.
**Calebbarnwell**: So my thought is let's just do an initial deposit before we start this project off and then let's do, you know, half up front and let's do half upon the final demo right before I transfer all the code to your direction.
**Calebbarnwell**: So you've got everything.
**Calebbarnwell**: And then maintenance is going to be, you know, for any bug fixes, any just general maintenance thing.
**Calebbarnwell**: I'm not just going to randomly do stuff, but if there's requested, like, hey, this is breaking for us, we need fixes on this, that's going to be 60 an hour just for my time to go and fix that, as well as server and AI costs, which I kind of put on the AI scope, the expectation for that, that's just based on how many tokens we use with Chat GPT.
**Calebbarnwell**: And I put an estimation on there as well.
**Bclymer**: I pay for ChatGPT.
**Bclymer**: Like we have an API thing we pay for.
**Calebbarnwell**: Okay, I'll see if it's possible.
**Bclymer**: Is that what you're talking about?
**Calebbarnwell**: Well, for OpenAI API, that's what we're going to be hooking up to.
**Calebbarnwell**: And if you go to the group AI Scope document and scroll down at the bottom for the Open API, they use tokens and they sort of.
**Calebbarnwell**: I think it's pretty much 1.5 or 2 tokens per word per prompt.
**Calebbarnwell**: And our prompts might be fairly sizable because we've got to include some of these, date some of the data that your team is using, and that's how it's going to learn.
**Calebbarnwell**: So if you go to that first document at the bottom, you'll see I'll have to help determine with you how many tokens per prompt and how many average prompts your team per month is doing.
**Calebbarnwell**: I estimate it's going to be several thousand tokens per prompt that we're doing.
**Calebbarnwell**: So every time your team asks a question to ChatGPT, it's going to be fed into the OpenAI API.
**Calebbarnwell**: We can determine which model works best for us.
**Calebbarnwell**: Maybe we don't need the smartest model.
**Calebbarnwell**: GPT 4.1.
**Calebbarnwell**: As you can see, it's $2 per 1 million tokens.
**Calebbarnwell**: Maybe we can use something like the Nano or something like that to save costs.
**Calebbarnwell**: We'll just have to test and see what actually works the best.
**Calebbarnwell**: But my understanding is that if we want to use the OpenAI API, we're going to have to do these tokens, and that's how they price it on the API.
**Calebbarnwell**: If there's any way that we can log into your account and use your PRO license, I'll let you know, Brandon.
**Calebbarnwell**: But my understanding with the API is that's how they charge separately.
**Bclymer**: Well, yeah, I mean, that's what I'm saying.
**Bclymer**: I pay for a separate API thing.
**Calebbarnwell**: API thing.
**Calebbarnwell**: Okay.
**Bclymer**: Yeah.
**Calebbarnwell**: You know how many tokens you get for that?
**Bclymer**: I don't know.
**Bclymer**: I.
**Bclymer**: I just have it to work auto re ups.
**Calebbarnwell**: Okay, well, let me look into that.
**Calebbarnwell**: I'm not going to charge you for anything that, you know, I'll log into your account as we set up this, this process and I'll stay in touch with you.
**Calebbarnwell**: Brad, I'm not just going to send you random bills for, for anything, but I'll make sure that I'm checking how many tokens you're getting access to and update.
**Bclymer**: And then, and then you mentioned.
**Calebbarnwell**: But for the IP agreement too, I wanted.
**Calebbarnwell**: I don't mean to cut you off, but I know you asked about that, so number six, we'll answer that.
**Calebbarnwell**: The way I had it set up is both you and I will retain joint intellectual property rights to this code base so you have full free.
**Calebbarnwell**: As I said, each party may use, extend or adapt the work product in the future.
**Calebbarnwell**: You can take it and do anything.
**Calebbarnwell**: Like you said, if I get hit by a bus in six months, it's all yours.
**Calebbarnwell**: Do as you will with it.
**Calebbarnwell**: But it also gives me the ability, since I'm basically doing this at the, the lowest price possible on my side, this allows me to also build the tool up on my side and be able to, to continue to work with it as well.
**Calebbarnwell**: So I think it's just in both of our best interests.
**Bclymer**: When you say utilize it on your side, like I mean this, this everything that we're teaching already uploading all that.
**Bclymer**: That is lito intellectual property.
**Calebbarnwell**: Yes, yes, that, that won't be included in none of your data.
**Calebbarnwell**: I'm not, I won't mess with it.
**Calebbarnwell**: And that's part of the confidentiality that we agree to keep all project related information confidential, not disclose any materials, data or trade secrets of third parties without written consent number seven.
**Calebbarnwell**: So that it would just be the actual like bare bones framework of this API tool and how generative AI project management can apply to other situations.
**Calebbarnwell**: I will never use your data, Brandon.
**Bclymer**: Okay, so all the, all the knowledge base that we're teaching this thing and learning.
**Bclymer**: Learning it.
**Calebbarnwell**: Yeah.
**Calebbarnwell**: Yes, that stays with you, Brandon.
**Bclymer**: Okay.
**Bclymer**: Yeah, okay, absolutely.
**Bclymer**: Okay, great.
**Bclymer**: And then so, so with that you mentioned bug fixes and stuff.
**Bclymer**: I guess my thought is though like hey, here's the demo, blah blah.
**Bclymer**: And four days later we're like using, it's like hey man, this isn't like working.
**Bclymer**: Right.
**Bclymer**: So I would expect that you would take care of that because this should be working now.
**Bclymer**: I understand if something, if I'm like hey man, change this.
**Calebbarnwell**: Yeah.
**Bclymer**: But as far as turning over a working product, absolutely.
**Calebbarnwell**: No, that makes sense to me.
**Calebbarnwell**: What we can do.
**Calebbarnwell**: I'll update this, Brandon, and differentiate from revisions and bug fixes.
**Calebbarnwell**: So I'll have it say on number nine, I'll update for bug fixes for in scope features within, you know, essentially if as long as you let me know bug fixes that you guys are having problems with within let's say the next 30 days after, you know, I submit the tool to you guys, I'll go ahead and get those fixed up.
**Calebbarnwell**: Outside of a maintenance revision rate, I.
**Bclymer**: I would say that the, the probably the best way to do that, and I'm sure you could do this pretty easy is somehow have like a ticketing thing because obviously everybody at the company is going to be using this.
**Bclymer**: And I cannot filter.
**Calebbarnwell**: No problem.
**Bclymer**: Here's this.
**Bclymer**: Like, hey, guys, if you have an issue, screenshot it, type the ticket thing into blah, blah, blah, and it'll send it to Caleb.
**Calebbarnwell**: Perfect.
**Calebbarnwell**: Perfect.
**Calebbarnwell**: What I'm going to do for that, Brandon, I'm going to host this thing in GitHub.
**Calebbarnwell**: That's where the actual code is going to live.
**Calebbarnwell**: Whenever I submit this, your direction at, we'll do the demo and then.
**Calebbarnwell**: And then we'll get the final payment and I will send you the code base.
**Calebbarnwell**: There's an issue tracker in GitHub, so you're also.
**Calebbarnwell**: I'll send some information about that, but your team can essentially just add issues.
**Calebbarnwell**: Like you said, ticket tracking.
**Calebbarnwell**: Here's a bug.
**Calebbarnwell**: If I own.
**Calebbarnwell**: Here's a bug I found.
**Calebbarnwell**: And again, anything.
**Calebbarnwell**: I mean, we're doing the minimum viable product to get this thing off the ground, but I want you guys to obviously have a working tool and we're not gonna, we're not gonna get to that point until your team is able to work with it and use it.
**Calebbarnwell**: So any of those in scope bugs I'll take care of.
**Calebbarnwell**: And then from there, as your team uses it, as we go forward, that's when I'll have that support rate.
**Calebbarnwell**: But then ideally, Brandon, if there's something else that, if you want to extend this product and add anything new to it, we can definitely just set up the next phase for the product.
**Calebbarnwell**: At that time, we can keep running with what we got.
**Calebbarnwell**: We'll just kind of see how.
**Calebbarnwell**: How it's working for your team.
**Bclymer**: Yeah.
**Bclymer**: I mean, the way that I would expect this to go.
**Calebbarnwell**: Yeah.
**Bclymer**: Is like, you know, like we talked about in phase, it's like, so here's phase one, right.
**Bclymer**: And at the end of the day, like, I'm sure you're.
**Bclymer**: You're really good at this, but I would doubt that you could test every single possible scenario to confirm there's no issues.
**Bclymer**: And so it's like, hey, we're going to do this, and then we're going to use it for two months where.
**Bclymer**: Whatever.
**Bclymer**: Like, and work out all the kinks.
**Bclymer**: Okay, this works.
**Bclymer**: All right, great.
**Bclymer**: Now we're going to kick off onto phase two.
**Calebbarnwell**: All right?
**Bclymer**: We've learned this, this and this.
**Bclymer**: Now we want to add in these features and change on that.
**Bclymer**: Because what I don't want to do is do it and then try to do something else.
**Bclymer**: And, oh, we didn't realize we had this issue.
**Bclymer**: And now it's an issue on top of an issue on top of an Issue.
**Calebbarnwell**: Absolutely.
**Calebbarnwell**: I'll be here too.
**Calebbarnwell**: Brandon.
**Calebbarnwell**: I'm not looking at this like, hey, you know, I'm gonna do this in six weeks.
**Calebbarnwell**: Here you go.
**Calebbarnwell**: And then I'm running off and doing, you know, doing my thing.
**Calebbarnwell**: I'll be here, you know, to chat with you and, and obviously give you everything you, you, you need.
**Calebbarnwell**: You've got all the IP rights and everything like that.
**Calebbarnwell**: But that, that's kind of my thought too is, you know, let's get the initial bug fixes out, but then as your team is using this, there's absolutely going to be things that you guys want to add in that, that you're learning from.
**Calebbarnwell**: And then, and then, then we set up kind of that phase two.
**Calebbarnwell**: We go add in anything that's necessary and we go from there.
**Calebbarnwell**: That's, that's the way I'm looking at this as well.
**Calebbarnwell**: I don't intend for this to be a, you know, catch and release type situation, you know, so.
**Bclymer**: Gotcha.
**Bclymer**: And then.
**Bclymer**: Yeah, yeah.
**Bclymer**: So yeah, if you want to update this and obviously, like you're just missing general information, like the client is not me, the client is the company, you know.
**Bclymer**: Yeah, yeah.
**Bclymer**: And then, yeah, I don't know if you're, if you have a company you're running stuff through, how you do it, but we'll need a W9 to get you set up as a vendor so that we can submit payment.
**Bclymer**: So whether that's personal or llc, it really doesn't matter.
**Calebbarnwell**: Okay.
**Calebbarnwell**: Yeah, yeah.
**Calebbarnwell**: If you have your own.
**Calebbarnwell**: I mean, what I've done in the past as an independent contractor is just submit invoices with PayPal.
**Calebbarnwell**: But if, yeah, you can, you can do that.
**Bclymer**: But per the IRS, like if I'm paying an independent contractor over 800, I've got to have W9.
**Calebbarnwell**: Okay, no problem, I'll get you that.
**Bclymer**: But you can, you can fill out a W9 and put your own social.
**Bclymer**: That's not a big deal.
**Bclymer**: I just have to have something that says whenever we do our taxes, hey, we paid these guys this much.
**Calebbarnwell**: No problem.
**Calebbarnwell**: No problem.
**Calebbarnwell**: So I will right after this meeting, then I'm going to send this over to you.
**Calebbarnwell**: So with the correct information, a leto group and, and let you kind of sign the document.
**Calebbarnwell**: I'll submit the PayPal invoice and then I'll get you that W9 as well.
**Calebbarnwell**: And then once, once that's all cleared up for both of our sides, we can get this thing kicked off.
**Calebbarnwell**: And then again, six week timeline is, is what kind of.
**Calebbarnwell**: I'm expecting if that works for you.
**Bclymer**: Yeah.
**Bclymer**: And then make sure to update the.
**Bclymer**: The intellectual property verbiage and, and call out a list of like, hey, I need admin access to the following items.
**Calebbarnwell**: Got you.
**Bclymer**: So whatever is, you know, our API, our notion, whatever, whatever.
**Calebbarnwell**: Okay, that sounds good.
**Calebbarnwell**: Through the process too, we can absolutely set up progress reports.
**Calebbarnwell**: You know, I'll keep you updated whether that you prefer email or you want to also have some in the middle progress meetings too.
**Calebbarnwell**: I'm totally good.
**Bclymer**: Yeah, I mean, we'll probably.
**Bclymer**: We'll probably have.
**Bclymer**: Like I said, I'd like to have progress meetings because.
**Calebbarnwell**: Yeah.
**Bclymer**: Hey, here's the front end thing because I'm going to want some of our branding guidelines involved in that.
**Bclymer**: Right.
**Bclymer**: So it's like, hey, here's what I expect it to look like, here's what I'm after.
**Bclymer**: And making sure that it looks like just a black screen with a text box is not going to work.
**Calebbarnwell**: Got you.
**Calebbarnwell**: This is an internal tool.
**Calebbarnwell**: Right.
**Calebbarnwell**: First and foremost, we'll get your branding on there and everything and make sure that this is looking the way that you want, Brandon.
**Calebbarnwell**: But I mean, again, on the front end, that's not where a lot of this project is focusing.
**Calebbarnwell**: So it's going to be bare bones and letting you know that now we can, we can definitely tie in your branding, make it look as pretty as possible.
**Bclymer**: Yeah, I mean, a standard text box, like, what, When I go to ChatGPT is fine.
**Calebbarnwell**: Okay.
**Bclymer**: But I just would like it to say, like, have our logo at the top left.
**Calebbarnwell**: No problem.
**Calebbarnwell**: No problem.
**Calebbarnwell**: That.
**Calebbarnwell**: That's, that's not an issue at all within this scope, so.
**Calebbarnwell**: But again, we'll meet as we go.
**Calebbarnwell**: That way you've got your ability to look at the product as we're going.
**Calebbarnwell**: We're not waiting till the end.
**Calebbarnwell**: Then you're like, oh, my God, we need to change all these things.
**Calebbarnwell**: You'll see it throughout.
**Calebbarnwell**: I'll try to at least, at the very least send weekly updates to your email too.
**Calebbarnwell**: And then we can schedule, you know, team calls, this as we go to Perfect.
**Calebbarnwell**: But that works for me.
**Calebbarnwell**: Brandon, if everything's sounding good on your end, we'll go ahead and get this thing kicked off.
**Calebbarnwell**: Anything else?
**Bclymer**: Nope, Just update all that stuff and make sure you cc Maria on it, please.
**Calebbarnwell**: Okay.
**Calebbarnwell**: Okay.
**Calebbarnwell**: Well, I appreciate it, man.
**Calebbarnwell**: I look forward to working together and getting this thing rolled out for you, getting your tickets.
**Calebbarnwell**: Appreciate you, Brandon.
**Calebbarnwell**: Take it easy.