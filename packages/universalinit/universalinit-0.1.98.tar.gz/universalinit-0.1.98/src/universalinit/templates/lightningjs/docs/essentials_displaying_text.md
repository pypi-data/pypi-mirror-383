# Displaying Text [​](#displaying-text){.header-anchor aria-label="Permalink to \"Displaying Text\""} {#displaying-text tabindex="-1"}

Besides displaying images, it is also very common to have *texts* in an
App.

Blits comes with a built-in `<Text>`-tag for displaying and styling
texts in a simple and intuitive way.

::: {.language-xml .vp-adaptive-theme}
[xml]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
<Text
  content="Hello world"
  font="ComicSans"
  size="$fontSize"
  :color="$changingColor"
/>
```
:::

You can use the Text-tag anywhere in your template, without the need to
explicitly import and register it in your Component.

## Available attributes on the Text tag [​](#available-attributes-on-the-text-tag){.header-anchor aria-label="Permalink to \"Available attributes on the Text tag\""} {#available-attributes-on-the-text-tag tabindex="-1"}

The Text-tag accepts the following attributes:

- `content` - the text to be displayed. Can be a hardcoded text, a
  dynamic value, or a reactive value
- `font` - the font family, defaults to `sans-serif`, or the default
  font specified in the launch settings
- `size` - the font size, defaults to `32`
- `color` - the color to display for the text, defaults to `white` and
  can be any of the supported Blits color formats (HTML, hexadecimal or
  rgb(a))
- `letterspacing` - letterspacing in pixels, defaults to `0`
- `align` - the alignment of the text, can be `left`, `right`, or
  `center`, defaults to `left`. Centering text and aligning text to the
  right requires the `maxwidth` attribute to be set as well.
- `maxwidth` - the max length of a line of text in pixels, words
  surpassing this length will be broken and wrapped onto the next line.
  This attribute is required when aligning center or right.
- `maxlines` - maximum number of lines that will be displayed
- `maxheight` - maximum height of a text block, lines that don\'t fit
  within this height will not be displayed
- `lineheight` - the spacing between lines in pixels
- `contain` - the strategy for containing text within the bounds, can be
  `none` (default), `width`, or `both`. In most cases, the value of this
  attribute will automatically be set by Blits, based on the other
  specified attributes
- `textoverflow` - the suffix to be added when text is cropped due to
  bounds limits, defaults to `...` (see more details
  [here](#text-overflow))

## Text dimensions [​](#text-dimensions){.header-anchor aria-label="Permalink to \"Text dimensions\""} {#text-dimensions tabindex="-1"}

When you want to center your Text element, or properly position other
Elements around your text, it is useful to know the exact dimensions of
your text.

Similar to the Image element (i.e. an Element with a `src`), Text
elements also accept the `@loaded` attribute. This event is called, as
soon as the text is rendered, and passes in the dimensions of the
generated text texture.

The example below shows how to use the `@loaded`-attribute to position
an Element as an underline, under a piece of text.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  template: `
    <Element>
      <Text :content="$myText" @loaded="$textLoaded" />
      <!-- gray underline -->
      <Element :w="$w" h="2" y="$y" color="#333" />
    </Element>
  `,
  props: ['myText'],
  state() {
    return {
      w: 0,
      y: 0,
    }
  },
  methods: {
    textLoaded(dimensions) {
      console.log(`The text has a width of ${dimensions.w} and a height of ${dimensions.h}`)
      // set the underline width to the exact width of the text
      this.w = dimensions.w
      // position the underline 8px below the text
      this.y = dimensions.h + 8
    }
  }
```
:::

## Text overflow [​](#text-overflow){.header-anchor aria-label="Permalink to \"Text overflow\""} {#text-overflow tabindex="-1"}

The text renderer offers the ability to display a *text overflow suffix*
when the text exceeds the bounds of the Text component.

This functionality is automatically enabled, but requires that both a
*horizontal* boundary (using `maxwidth`) and a *vertical* boundary
(using `maxlines` or `maxheight`) are specified on the Text component.

The `textoverflow`-attribute itself is not required, unless you want to
use another suffix than the standard `...`. If you want *no suffix* (and
just a hard cutoff), the`textoverflow`-attribute should be set to
`false` or an *empty string*.

## SDF and Canvas2d [​](#sdf-and-canvas2d){.header-anchor aria-label="Permalink to \"SDF and Canvas2d\""} {#sdf-and-canvas2d tabindex="-1"}

Compared to Lightning 2, texts have improved a lot in Lightning 3,
thanks to the SDF (Signed Distance Field) Text renderer.

With the SDF text renderer, texts appear a lot *sharper* on screen. The
SDF technique also allows for better scaling of texts, without them
becoming blurry - a well-known painpoint in Lightning 2 Apps.

In general, it\'s recommended to use the SDF text renderer, but
Lightning 3 still has a Canvas2d text renderer as a backup, and you can
use both text renderers within the same App.

## Using custom fonts [​](#using-custom-fonts){.header-anchor aria-label="Permalink to \"Using custom fonts\""} {#using-custom-fonts tabindex="-1"}

The `font`-attribute on the `<Text>`-tag is used to define which font
family should be used for a certain piece of text.

When you create a new Blits app using the available [getting started
boilerplate](./../getting_started/getting_started.html) you\'ll be able
to use the `lato` (Lato regular) and `raleway` (Raleway ExtraBold) fonts
out of the box.

But of course, you can also use any custom font that you want, to give
your App the unique look and feel that fits with the design.

Adding a custom font to a Blits App is quite straightforward. First,
you\'ll need to place a `.ttf`, `.woff` or `.otf` version of your font
in the `public` folder (i.e. `public/fonts/comic-sans.ttf`).

Then you\'ll need to register the custom font in the Launch settings of
your app (in `src/index.js`). The `fonts`-key in the settings is an
`Array` that specifies all available fonts in your App.

Just add a new font object with the necessary details:

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
  fonts: [
    // ...
    {
      family: 'ComicSans', // the font name used in your App
      type: 'msdf', // type of text renderer to use (msdf or web)
      file: 'fonts/Comic-Sans.ttf', // location of the ttf file
    },
    // ..
  ],
```
:::

From this moment on you\'ll be able to use the font `ComicSans` anywhere
in your App:

::: {.language-xml .vp-adaptive-theme}
[xml]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
<Text font="ComicSans" content="I'm Comic Sans font!" />
```
:::

### Custom characters [​](#custom-characters){.header-anchor aria-label="Permalink to \"Custom characters\""} {#custom-characters tabindex="-1"}

For MSDF font, a font atlas is created. By default this atlas includes
all printable main ASCII characters. If you know beforehand that you
won\'t need certain characters, it would be more optimal to generate
only those characters that are actually needed.

Similarly, if you need characters outside of the default set, like
accents or other special characters, then these will need to be included
in the generated font atlas.

In order to control which characters are generated for a specific font,
you can add a *font config file* per font inside the `assets/fonts`
folder. Its name should match the name of the font file, like so:
`myfont.config.json`.

The config file should look something like this:

::: {.language-json .vp-adaptive-theme}
[json]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
{
  "charset": "0123456789éåaü"
}
```
:::

With the configuration above, only numbers and the specified letters
with accents will be generated (i.e. the default character set is
overwritten).

> Please note that only special characters and accents that are part of
> the original font can be added to the generated font atlas. Other
> characters will show up as a `?`.
