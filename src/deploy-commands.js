const { SlashCommandBuilder } = require('@discordjs/builders');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const { devID, devServerID, token } = require('../json/config.json');

const commands = [
    new SlashCommandBuilder().setName('setrole').setDescription('Set the Role that new users will recieve'),
    new SlashCommandBuilder().setName('ping').setDescription('Ping the Bot!')
].map(command => command.toJSON());

const rest = new REST({ version: '9'}).setToken(token);

rest.put(Routes.applicationGuildCommands(devID, devServerID), { body: commands })
    .then(() => console.log('Successfully registered application commands.'))
    .catch(console.error);