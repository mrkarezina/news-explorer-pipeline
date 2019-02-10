

request={
    'text': """
    
    Howdy Moz readers,

I'm Russ Jones, Principal Search Scientist at Moz, and I am excited to announce a fantastic upgrade coming next month to one of the most important metrics Moz offers: Domain Authority.

Domain Authority has become the industry standard for measuring the strength of a domain relative to ranking. We recognize that stability plays an important role in making Domain Authority valuable to our customers, so we wanted to make sure that the new Domain Authority brought meaningful changes to the table.

Learn more about the new DA

What’s changing?
What follows is an account of some of the technical changes behind the new Domain Authority and why they matter.

The training set:
Historically, we’ve relied on training Domain Authority against an unmanipulated, large set of search results. In fact, this has been the standard methodology across our industry. But we have found a way to improve upon it fundamentally, from the ground up, making Domain Authority more reliable. In particular, the new Domain Authority is better at understanding sites which don't rank for any keywords at all than it has in the past.

The training algorithm:
Rather than relying on a complex linear model, we’ve made the switch to a neural network. This offers several benefits including a much more nuanced model which can detect link manipulation.

The model factors:
We have greatly improved upon the ranking factors behind Domain Authority. In addition to looking at link counts, we’ve now been able to integrate our proprietary Spam Score and complex distributions of links based on quality and traffic, along with a bevy of other factors.

The backbone:
At the heart of Domain Authority is the industry's leading link index, our new Moz Link Explorer. With over 35 trillion links, our exceptional data turns the brilliant statistical work by Neil Martinsen-Burrell, Chas Williams, and so many more amazing Mozzers into a true industry leading standard.

What does this mean?
These fundamental improvements to Domain Authority will deliver a better, more trustworthy metric than ever before. We can remove spam, improve correlations, and, most importantly, update Domain Authority relative to all the changes that Google makes.

It means that you will see some changes to Domain Authority when the launch occurs. We staked the model to our existing Domain Authority which minimizes changes, but with all the improvements there will no doubt be some fluctuation in Domain Authority scores across the board.

What should we do?
Use DA as a relative metric, not an absolute one.
First, make sure that you use Domain Authority as a relative metric. Domain Authority is meaningless when it isn't compared to other sites. What matters isn't whether your site drops or increases — it's whether it drops or increases relative to your competitors. When we roll out the new Domain Authority, make sure you check your competitors' scores as well as your own, as they will likely fluctuate in a similar direction.

Know how to communicate changes with clients, colleagues, and stakeholders
Second, be prepared to communicate with your clients or webmasters about the changes and improvements to Domain Authority. While change is always disruptive, the new Domain Authority is better than ever and will allow them to make smarter decisions about search engine optimization strategies going forward.

Expect DA to keep pace with Google
Finally, expect that we will be continuing to improve Domain Authority. Just like Google makes hundreds of changes to their algorithm every year, we intend to make Domain Authority much more responsive to Google's changes. Even when Google makes fundamental algorithm updates like Penguin or Panda, you can feel confident that Moz's Domain Authority will be as relevant and useful as ever.

When is it happening?
We plan on rolling out the new Domain Authority on March 5th, 2019. We will have several more communications between now and then to help you and your clients best respond to the new Domain Authority, including a webinar on February 21st. We hope you’re as excited as we are and look forward to continuing to bring you the most reliable, cutting-edge metrics our industry has to offer.

Be sure to check out the resources we’ve prepared to help you acclimate to the change, including an educational whitepaper and a presentation you can download to share with your clients, team, and stakeholders:
    
    """
}

import requests

r = requests.post("https://us-central1-graph-intelligence.cloudfunctions.net/language-processor", json=request)

print(r.status_code, r.reason)
print(r.text)