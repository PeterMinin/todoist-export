# Export for Todoist

A Node.js application to backup Todoist data as JSON or CSV.

<div align="center">

![Screenshot](screenshot.png)

✨ **[Live demo](https://darekkay.com/todoist-export/)** ✨

</div>

## Development

### Quick Start

1. Create a [Todoist App](https://developer.todoist.com/appconsole.html). On localhost use `http://localhost:3000/todoist-export/` for both "App Service URL" and "OAuth Redirect URL".

2. Copy `src/config.js.example` to `src/config.js` and fill in the id and secret from the created app.

3. Install required packages (you can use `npm` instead of `yarn`):

```
yarn install
```

4. Start server:

```
yarn start
```

Refer to the [API](https://developer.todoist.com/) for more information.

### Configure SSL

Todoist redirects to a HTTPS version of your OAuth Redirect URL, even if a HTTP URL is defined. To retrieve your Todoist backup, you can change the URL from HTTPS to HTTP in the browser address bar after authorization. You can also start the app as HTTPS server, after creating a self-signed SSL certificate and defining your certificate data in `config.js`:

```
ssl: {
    cert: fs.readFileSync('./ssl/fullchain.pem'),
    key: fs.readFileSync('./ssl/privkey.pem'),
    passphrase: 'ssl certificate passphrase'
}
```

## License

Copyright 2014-2021 Darek Kay <hello@darekkay.com>

This project and its contents are open source under the [MIT license](LICENSE).
