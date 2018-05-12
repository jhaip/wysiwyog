package main

import "fmt"
import "time"
import "math"
import "strconv"
import "strings"
import "github.com/kokardy/listing"
// import "image/color"
// import "github.com/mattn/go-ciede2000"

func main() {
  start := time.Now()
  colors := [][3]int{[3]int{153,146,122}, [3]int{124,128,175}, [3]int{132,133,165}, [3]int{138,136,176}, [3]int{134,130,165}, [3]int{170,40,48}, [3]int{100,71,83}}
  // answer = "GBBBBRD" aka "1222203"
  colorGroups := groupColors(colors)
  cornerId := identifyColorGroups(colors, colorGroups)
  elapsed := time.Since(start)
  fmt.Printf("took %s \n", elapsed)
  fmt.Println("Corner ID: ", cornerId)
}

type P struct {
  G [][]int
  U []int
  score float64
}

func getColorDistance(a, b [3]int) float64 {
  return math.Abs(float64(a[0]-b[0])) + math.Abs(float64(a[1]-b[1])) + math.Abs(float64(a[2]-b[2]))
  // using CIEDE2000 color diff is 5x slower than RGB diff (almost 2ms for one corner)
  // c1 := &color.RGBA{
  //   uint8(a[0]),
  //   uint8(a[1]),
  //   uint8(a[2]),
  //   255,
  // }
  // c2 := &color.RGBA{
  //   uint8(b[0]),
  //   uint8(b[1]),
  //   uint8(b[2]),
  //   255,
  // }
  // return ciede2000.Diff(c1, c2)
}

func groupColors(colors [][3]int) P {
  // color_combinations := combinations_as_list(7, 4)
  color_combinations := listing.Combinations(
    listing.IntReplacer([]int{0,1,2,3,4,5,6}), 4, false, 7,
  )
  // fmt.Println(color_combinations)

  minScore := -1.0
  var bestGroup P
  for rr := range color_combinations {
    r := rr.(listing.IntReplacer)
    p := P{G: [][]int{[]int{r[0]}, []int{r[1]}, []int{r[2]}, []int{r[3]} }}
    // Fill p.U with unused #s
    for i := 0; i < 7; i += 1 {
      if r[0] != i && r[1] != i && r[2] != i && r[3] != i {
        p.U = append(p.U, i)
      }
    }
    // pop of each element in p.U and add to closet colored group
    for i := 0; i < 3; i += 1 {
      u_color := colors[p.U[0]]
      // add element to group closest in color
      min_i := 0
      min := getColorDistance(u_color, colors[r[0]])
      for j := 1; j < 4; j += 1 {
        d := getColorDistance(u_color, colors[r[j]])
        if d < min {
          min = d
          min_i = j
        }
      }
      p.G[min_i] = append(p.G[min_i], p.U[0])
      p.U = p.U[1:]
      p.score += min
    }

    // fmt.Println(p)

    // Keep track of the grouping with the lowest score
    if minScore == -1 || p.score < minScore {
      minScore = p.score
      bestGroup = p
    }
  }

  // fmt.Println("Best group", bestGroup)
  return bestGroup
}

func identifyColorGroups(colors [][3]int, group P) string {
  color_templates := listing.Permutations(
    listing.IntReplacer([]int{0,1,2,3}), 4, false, 4,
  )
  // fmt.Println(color_templates)

  calibration := [][3]int{[3]int{255, 0, 0}, [3]int{0, 255, 0}, [3]int{0, 0, 255}, [3]int{0, 0, 0}}
  // calibration := make([][3]int, 4)
  // calibration[0] = [3]int{190, 55, 49}  // red
  // calibration[1] = [3]int{168, 164, 145}  // green
  // calibration[2] = [3]int{148, 151, 190}  // blue
  // calibration[3] = [3]int{113, 72, 96}  // dark

  minScore := -1.0
  var bestMatch []int  // index = color, value = index of group in P that matches color
  for rr := range color_templates {
    r := rr.(listing.IntReplacer)
    score := 0.0
    score += getColorDistance(calibration[0], colors[group.G[r[0]][0]])
    score += getColorDistance(calibration[1], colors[group.G[r[1]][0]])
    score += getColorDistance(calibration[2], colors[group.G[r[2]][0]])
    score += getColorDistance(calibration[3], colors[group.G[r[3]][0]])
    // fmt.Println(r, score)
    if minScore == -1 || score < minScore {
      minScore = score
      bestMatch = r
    }
  }

  // fmt.Println("best match", bestMatch)

  result := make([]string, 7)
  for i, g := range bestMatch {
    for _, k := range group.G[g] {
      result[k] = strconv.Itoa(i)
    }
  }
  // fmt.Println("Result", result)  // Something like "1222203"

  return strings.Join(result, "")
}
