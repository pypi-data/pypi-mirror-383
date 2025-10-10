# Text-to-Speech / Announcer [​](#text-to-speech-announcer){.header-anchor aria-label="Permalink to \"Text-to-Speech / Announcer\""} {#text-to-speech-announcer tabindex="-1"}

Blits comes with a built-in Text-to-Speech / Announcer functionality, to
easily make your App more accessible. This is something that\'s often
overlooked when developing an App, but having speech assistance
integrated into your App is a huge deal for those users who are visually
impaired.

## Integrated with the router [​](#integrated-with-the-router){.header-anchor aria-label="Permalink to \"Integrated with the router\""} {#integrated-with-the-router tabindex="-1"}

The Announcer in Blits is directly integrated with the router
functionality. This means that through simple configuration, a
descriptive message can be announced, when navigating from page to page,
without the need for adding extra custom code.

Just add an `announce` key in the configuration of your route, that
contains the message you would like to be announced when visiting that
route.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
const routes = [
  // ...
  {
    path: '/settings',
    component: Settings,
    announce: "Welcome to the Settings page",
  },
  // ...
]
```
:::

## Custom announcement messages [​](#custom-announcement-messages){.header-anchor aria-label="Permalink to \"Custom announcement messages\""} {#custom-announcement-messages tabindex="-1"}

Furthermore, it\'s possible to speak out custom messages anywhere in
your App logic, for example when a component receives focus, as a
reaction to user input, or to announce error messages when a remote API
call fails.

Each component in Blits has a `this.$announcer.speak()` available, which
accepts a `string` with the message to be announced.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
Blits.Component('MyComponent', {
  // ...
  hooks: {
    focus() {
      this.$announcer.speak('MyComponent just got focus')
    }
  },
  keys: {
    right() {
      if(this.focused === this.items.length - 1) {
        this.$announcer.speak('End of row reached')
      } else {
        //
      }
    }
  }
})
```
:::

### Execute logic when done [​](#execute-logic-when-done){.header-anchor aria-label="Permalink to \"Execute logic when done\""} {#execute-logic-when-done tabindex="-1"}

The `speak()`-function returns a promise that resolves when it\'s done
speaking, or when it\'s interupted or errors out. The reason of the
`speak()` method resolving is passed as an argument into the resolve
function.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
this.$announcer.speak('Hello').then((reason) => console.log('Speaking hello finished', reason))
```
:::

### Announcement queue [​](#announcement-queue){.header-anchor aria-label="Permalink to \"Announcement queue\""} {#announcement-queue tabindex="-1"}

The `speak()`-method places the messages in an announcement queue and
then starts processing that queue. That means that when the queue is
empty, it will instantly announce the messages passed. If there are
other messages in the queue, the messages will be spoken when all
previous messages are announced.

Optionally you can set the politeness of a message to `assertive` and
pass it a the second argument of the `speak()`-method.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
this.$announcer.speak('Very important message that should get priority', 'assertive')
```
:::

This will place the message at the beginning of the queue, making in the
first message to be announced after the current message (if any) has
finished.

#### Clearing and interupting [​](#clearing-and-interupting){.header-anchor aria-label="Permalink to \"Clearing and interupting\""} {#clearing-and-interupting tabindex="-1"}

Since each message added into the queue may take a bit of time to
actually be announced, it\'s possible that the user has navigated
elsewhere in the mean time, making the queued up messages not relevant.

The announcer plugin allows you to clear the entire queue by calling
`this.$announcer.clear()`. Additionally if you want to interup the
messages being currently spoken, the announcer plugin offers the
`this.$announcer.stop()`-method.

#### Canceling individual messages [​](#canceling-individual-messages){.header-anchor aria-label="Permalink to \"Canceling individual messages\""} {#canceling-individual-messages tabindex="-1"}

In some cases you may not want to clear the entire queue, but instead
cancel out a single message.

Imagine an App with a row of tiles, it\'s possible that before the title
of the role is being spoken out, the user already navigates through the
tiles within the row. Traditionally you\'d use the focus event to speak
out info about each tile (i.e. adding tot the queue). You don\'t want
all previously focused tiles to still be announced, but would still want
the category of the row to be announced, making clearing the queue not
required.

The `speak()`-method return a Promise that also contains a `cancel()`
function. When called, it will cancel that specific message and remove
it from the queue before it can be spoken out.

Additionally if you want to *interrupt* a specific messages as it\'s
being spoken out as well and go straight to the next message in the
queue (i.e. the newly focused item, for example). You can use the
`stop()` message that is returned on the Promise returned by the
`speak()`-method.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
Blits.Component('MyTile', {
  //
  props: ['title'],
  state() {
    return {
      message: null
    }
  },
  hooks: {
    focus() {
      // add message to the announcement queue
      this.message = this.$announcer.speak(`This is tile ${this.title}`)
    },
    unfocus() {
      // when unfocused interrupt the message if it's already being spoken out
      this.message.stop()
      // and cancel the message to remove it from the queue
      this.message.cancel()
    }
  }
})
```
:::

## Enabling / disabling the announcer [​](#enabling-disabling-the-announcer){.header-anchor aria-label="Permalink to \"Enabling / disabling the announcer\""} {#enabling-disabling-the-announcer tabindex="-1"}

By default the announcer is disabled. This means that whenever you call
`this.$announcer.speak()` there will actually not be anything spoken out
via the Text To Speech engine.

In order to enable utterances being spoken out, you can set the Blits
launch setting `announcer` to `true` in the index.js.

Alternatively the announcer can be enabled or disabled run time by using
one of the following methods on the Announcer pluging:

- `this.$announcer.enable()` - activates the announcer
- `this.$announcer.disable()` - deactivates the announcer
- `this.$announcer.disable(true/false)` - turns the announcer or on off
