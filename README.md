# Neptune's Pride Alert

My first (and possibly last) game of Neptune's Pride I was in the early stages of a brutal conflict with the savvy dictator Le Loi. The war was teetering on a knife's edge and one wrong move or missed order would spell disaster. Therefore, it was in the best interest of the galaxy that I set my alarm for 3am in order to see if my tricksy foe would dare launch in the dead of night (spoiler alert: he did). I realized then three things:

1. The fight for control of the galaxy was going to take a very long time
2. If I have to wake up every night just to see if I'm being attacked, I will likely suffer from sleep deprevation within days
3. I'm a software engineer, there's a better way to do this

It was with this burst of insight that I decided to write an AWS lambda to check at the start of each cycle whether any new ships are coming at my stars, and if so send a text to me so I'll know right away. Combined with iOS's Emergency Bypass, this meant I would never miss a surprise attack again, nor will I have to needlessly set an alarm for the middle of the night.

### DISCLAIMER

This is pretty much the first python, AWS lambda and dynamoDB code I have ever written (individually or together) so it's probably pretty :poop:. But it works!

## How Can I Use This

First, consider not playing Neptune's Pride. It's stressful, time consuming, and potentially ruinous of relationships.

Ok, now that you've ignored that advice, you should know up front that this is not a hosted service. You have to run your own lambda with your own Twilio account (or branch this repo and do whatever you want, it's a free Internet).

The good news is that's both easy and free\*. It just takes a few minutes of configuration which I'll detail below. First, sign into Neptune's Pride and make note of your game number. You can easily find this in the URL of your game.

Next, [sign up for a Twilio account](https://www.twilio.com/try-twilio). Once signed up make note of your `Account SID` and `Auth Token`, you'll need both when setting up your lambda environ.

Finally, [sign up for an AWS account](https://portal.aws.amazon.com/billing/signup#/start). Once that's done it's time to create your lamdba.

1. Search for the lambda product
2. Click `Create function`
3. Choose Blueprints and search for `hello-world-python3`
4. Name your function whatever you want
5. Choose `Create new role from template(s)` and enter any role name you want
6. Under `Policy templates` choose `Simple microservice permissions`
7. Click `Create function`
8. In the `Function code` section below, either copy and paste the code from this repo, or download the zip archive and upload it
9. In the `Environment variables` section, configure the following:
    a. `GAME_NUMBER`: The Neptune's Pride game number from above
    b. `USERNAME`: Your Neptune's Pride username
    c. `PASSWORD`: Your Neptune's Pride password
    d. `TWILIO_FROM`: The Twilio phone number you created to send text messages from
    e. `TWILIO_TO`: The phone number you want to send text messages to (i.e. your cell)
    f. `TWILIO_ACCOUNT_SID`: From above
    g. `TWILIO_AUTH_TOKEN`: From above
10. You're nearly there! Next we have to give your lambda permissions to create dynamoDB tables (the default policy we added only gives permissions to modify rows, not tables).
11. Towards the top of the screen in the `Designer` section, click on `Amazon DynamoDB` (it should be below and to the right of your named lambda) and scroll down a bit
12. Click on the link to the IAM console
13. You should see a policy named something like `AWSLambdaMicroserviceExecutionRole...`, click the arrow to the left of that
14. You should see a DynamoDB service with a *Limited* access level. We're gonna fix that right up
15. Click `Edit Policy`
16. Click `Add additional permissions`
17. `Service`: `DynamoDB`
18. Check `All DynamoDB actions`
19. Click `Review policy`
20. Click `Save changes`
21. Ok, all done with your permissions! Close this tab
22. Back on your lambda, it should be fully functioning. You can test it by clicking the `Test` button. If you don't actually have any enemy ships coming at your stars you'll see it execute, print some light debugging code and exit. If you do have enemy ships coming at you, you should receive a text in a few moments.
23. Now we have to schedule this lambda to run on the hour after your game `ticks`
24. Back in the `Designer` section, click `CloudWatch Events`
25. Scroll down a bit and select `Create new rule`
26. Name it what you want
27. Select `Schedule expression`
28. Enter an expression similar to `cron(55 * * * ? *)` replacing `55` with whatever minute mark (plus a minute or two) that your game ticks at. For example, my current game ticks around the `50` minute mark so I used `55` just to be safe.
29. Click `Add`

Now you are for real all done! If you're being attacked, at whatever minute mark you selected in step `28` above you should receive a text message telling you what ships are coming at you! Have fun conquering the galaxy!
