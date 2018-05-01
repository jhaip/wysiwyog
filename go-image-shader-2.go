package main

import (
  zmq "github.com/pebbe/zmq4"

  "fmt"
	"image"
	"image/draw"
	_ "image/png"
	"os"

	"github.com/faiface/glhf"
	"github.com/faiface/mainthread"
	"github.com/go-gl/glfw/v3.1/glfw"
  "github.com/go-gl/mathgl/mgl32"
  "github.com/pixiv/go-libjpeg/rgb"
)

// Modified source from github.com/faiface/glhf/examples/demo/main.go
// I added in zmq and image creation stuff

func loadImage(path string) (*image.NRGBA, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	img, _, err := image.Decode(file)
	if err != nil {
		return nil, err
	}
	bounds := img.Bounds()
	nrgba := image.NewNRGBA(image.Rect(0, 0, bounds.Dx(), bounds.Dy()))
	draw.Draw(nrgba, nrgba.Bounds(), img, bounds.Min, draw.Src)
	return nrgba, nil
}

func convertFrameToImage(frame []byte) (*image.NRGBA, error) {
  img := rgb.NewImage(image.Rect(0, 0, 1280, 720))
  img.Pix = frame
  bounds := img.Bounds()
	gopherImage := image.NewNRGBA(image.Rect(0, 0, bounds.Dx(), bounds.Dy()))
	draw.Draw(gopherImage, gopherImage.Bounds(), img, bounds.Min, draw.Src)
  return gopherImage, nil
}

func getFrameData() ([]byte, error) {
  fmt.Println("Connecting to hello world server...")
	requester, _ := zmq.NewSocket(zmq.REQ)
	defer requester.Close()
	requester.Connect("tcp://localhost:5555")

  // send hello
  msg := "{\"event\": \"get_image\", \"options\": {}}"
  fmt.Println("Sending ", msg)
  requester.Send(msg, 0)

  // Wait for reply:
	total := 0  //  Total bytes received
	chunks := 0 //  Total chunks received
  var frameSave []byte

	for {
		frame, err := requester.RecvBytes(0)
		if err != nil {
      fmt.Printf("error %v\n", err)
			break //  Shutting down, quit
		}
    fmt.Printf("size: %v\n", len(frame))
    frameSave = append(frameSave, frame...)
    fmt.Printf("size save: %v\n", len(frameSave))
		chunks++
		size := len(frame)
		total += size

		if size == 0 {
      fmt.Printf("break\n")
			break //  Whole file received
		}
	}
	fmt.Printf("%v chunks received, %v bytes\n", chunks, total)
  fmt.Printf("size: %v\n", len(frameSave))

  return frameSave, nil
}

func run() {
	var win *glfw.Window

	defer func() {
		mainthread.Call(func() {
			glfw.Terminate()
		})
	}()

	mainthread.Call(func() {
		glfw.Init()

		glfw.WindowHint(glfw.ContextVersionMajor, 3)
		glfw.WindowHint(glfw.ContextVersionMinor, 3)
		glfw.WindowHint(glfw.OpenGLProfile, glfw.OpenGLCoreProfile)
		glfw.WindowHint(glfw.OpenGLForwardCompatible, glfw.True)
		glfw.WindowHint(glfw.Resizable, glfw.False)

		var err error

		win, err = glfw.CreateWindow(1280, 720, "GLHF Rocks!", nil, nil)
		if err != nil {
			panic(err)
		}

		win.MakeContextCurrent()

		glhf.Init()
	})

	var (
		// Here we define a vertex format of our vertex slice. It's actually a basic slice
		// literal.
		//
		// The vertex format consists of names and types of the attributes. The name is the
		// name that the attribute is referenced by inside a shader.
		vertexFormat = glhf.AttrFormat{
			{Name: "position", Type: glhf.Vec2},
			{Name: "texture", Type: glhf.Vec2},
		}

    uniformFormat = glhf.AttrFormat{
			{Name: "iChannelResolution", Type: glhf.Vec3},
		}

		// Here we declare some variables for later use.
		shader  *glhf.Shader
		texture *glhf.Texture
		slice   *glhf.VertexSlice
	)

	// Here we load an image from a file. The loadImage function is not within the library, it
	// just loads and returns a image.NRGBA.
	// gopherImage, err := loadImage("celebrate.png")
	// if err != nil {
	// 	panic(err)
	// }

  loadedFrame, err := getFrameData()
  if err != nil {
		panic(err)
	}

  gopherImage, err := convertFrameToImage(loadedFrame)
	if err != nil {
		panic(err)
	}

	// Every OpenGL call needs to be done inside the main thread.
	mainthread.Call(func() {
		var err error

		// Here we create a shader. The second argument is the format of the uniform
		// attributes. Since our shader has no uniform attributes, the format is empty.
    // ^ not true anymore, I added uniformFormat to pass in a uniform
		shader, err = glhf.NewShader(vertexFormat, uniformFormat, vertexShader, fragmentShader)

		// If the shader compilation did not go successfully, an error with a full
		// description is returned.
		if err != nil {
			panic(err)
		}

		// We create a texture from the loaded image.
		texture = glhf.NewTexture(
			gopherImage.Bounds().Dx(),
			gopherImage.Bounds().Dy(),
			true,
			gopherImage.Pix,
		)

    // Assign uniform value
    shader.SetUniformAttr(0, mgl32.Vec3{1280, 720, 0})

		// And finally, we make a vertex slice, which is basically a dynamically sized
		// vertex array. The length of the slice is 6 and the capacity is the same.
		//
		// The slice inherits the vertex format of the supplied shader. Also, it should
		// only be used with that shader.
		slice = glhf.MakeVertexSlice(shader, 6, 6)

		// Before we use a slice, we need to Begin it. The same holds for all objects in
		// GLHF.
		slice.Begin()

		// We assign data to the vertex slice. The values are in the order as in the vertex
		// format of the slice (shader). Each two floats correspond to an attribute of type
		// glhf.Vec2.
		slice.SetVertexData([]float32{
			-1, -1, 0, 1,
			+1, -1, 1, 1,
			+1, +1, 1, 0,

			-1, -1, 0, 1,
			+1, +1, 1, 0,
			-1, +1, 0, 0,
		})

		// When we're done with the slice, we End it.
		slice.End()
	})

	shouldQuit := false
	for !shouldQuit {
		mainthread.Call(func() {
			if win.ShouldClose() {
				shouldQuit = true
			}

			// Clear the window.
			glhf.Clear(1, 1, 1, 1)

			// Here we Begin/End all necessary objects and finally draw the vertex
			// slice.
      shader.SetUniformAttr(0, mgl32.Vec3{1280, 720, 0})
			shader.Begin()
      shader.SetUniformAttr(0, mgl32.Vec3{1280, 720, 0})
			texture.Begin()

			slice.Begin()
			slice.Draw()
			slice.End()
			texture.End()
			shader.End()

			win.SwapBuffers()
			glfw.PollEvents()
		})
	}
}

func main() {
	mainthread.Run(run)
}

var vertexShader = `
#version 330 core

in vec2 position;
in vec2 texture;

out vec2 Texture;

void main() {
	gl_Position = vec4(position, 0.0, 1.0);
	Texture = texture;
}
`

var fragmentShader2 = `
#version 330 core

in vec2 Texture;

out vec4 color;

uniform sampler2D tex;
uniform vec3 iChannelResolution;

void main() {
  vec2 onePixel = vec2(1.0, 1.0) / vec2(iChannelResolution[0], iChannelResolution[1]);
  vec2 textCoord = gl_FragCoord.xy / vec2(iChannelResolution[0], iChannelResolution[1]);
	// color = texture(tex, Texture);
  color = vec4(textCoord[0], textCoord[0], textCoord[0], 1.0);
}
`


// var dotsShader = `
var fragmentShader = `
#version 330 core

#define u_r 3.0
#define M_PI 3.1415926535897932384626433832795
#define PHI_STEP 10.0*M_PI/180.0

in vec2 Texture;

out vec4 color;

uniform sampler2D tex;
uniform vec3 iChannelResolution;

float getLum(in vec4 pix) {
    vec3 lum = vec3(0.299, 0.587, 0.114);
    return dot( pix.rgb, lum);
}

void main() {
  vec2 onePixel = vec2(1.0, 1.0) / vec2(iChannelResolution[0], iChannelResolution[1]);
  vec2 textCoord = gl_FragCoord.xy / vec2(iChannelResolution[0], iChannelResolution[1]);
  // vec4 middle = texture(tex, Texture);
  vec4 middle = texture(tex, textCoord);
  float middleLum = getLum(middle);
  float sum = 0.0;
  float pointLum = 0.0;
	float phi = 0.0;

  for (int i = 0; i < 36; i+=1)
	{
		phi += PHI_STEP;
    pointLum = getLum(texture(tex, textCoord + onePixel*vec2(u_r*cos(phi), u_r*sin(phi))));
		sum += pointLum - middleLum;
	}

  float sumAvg = sum / 36.0;
  float stdDev = 0.0;
  phi = 0.0;

  for (int i = 0; i < 36; i+=1)
	{
		phi += PHI_STEP;
    pointLum = getLum(texture(tex, textCoord + onePixel*vec2(u_r*cos(phi), u_r*sin(phi))));
		stdDev += ((pointLum - middleLum) - sumAvg)*((pointLum - middleLum) - sumAvg);
	}

  stdDev = stdDev / 36.0;
  color = vec4(sumAvg*(1.0/(stdDev*50.0+1.0)));
}
`
