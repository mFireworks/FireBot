const { Client, Intents } = require('discord.js');
const { token } = require('./config.json');

// Create new client instance
const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

// When client is ready, we'll run this once
client.once('ready', () => {
    console.log('Ready!');
});

client.login(token);