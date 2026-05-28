require('dotenv').config();

const twilio = require('twilio');

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const fromNumber = process.env.TWILIO_PHONE_NUMBER;
const toNumber = process.env.TWILIO_TEST_TO || '+216XXXXXXXX';

async function main() {
  if (!accountSid || !authToken || !fromNumber) {
    throw new Error('Missing Twilio environment variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER');
  }

  const client = twilio(accountSid, authToken);
  const message = await client.messages.create({
    body: 'Test Twilio OK',
    from: fromNumber,
    to: toNumber,
  });

  console.log(message.sid);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});