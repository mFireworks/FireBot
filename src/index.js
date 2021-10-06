const { Client, Intents } = require('discord.js');
const { token } = require('../json/config.json');

// Create new client instance
const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

// When client is ready, we'll run this once
client.once('ready', () => {
    console.log('Ready!');
});

client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand())
        return;

    const { commandName } = interaction;

    if (commandName === 'ping') {
        await interaction.reply('Pong!');
    }
});

client.login(token);