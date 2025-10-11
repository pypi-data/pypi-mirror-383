import sys
from pathlib import Path

import numpy as np
import numpy.random as npr
import numpy.testing as npt
import pytest

import delta
from delta import data, imgops

# fmt: off
MASK_1D = np.array(
    [
        [
            0, 1,
            0, 0, 0, 1, 1, 0, 1, 1,
            0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1,
        ]
    ]
)
DISTS_1D = np.array(
    [
        [
            6, 0,
            4, 4, 4, 0, 0, 2, 0, 0,
            5, 6, 6, 6, 4, 0, 2, 0, 3, 3, 0, 0, 0, 3, 3, 0, 2, 0, 0, 0, 2, 0, 0, 0,
        ]
    ]
)

SEG_DEFORM = np.array(
    [
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
        [1, 0, 1, 1, 0, 0, 1, 1, 1, 0],
        [0, 0, 1, 1, 0, 0, 1, 1, 1, 1],
        [0, 1, 1, 0, 0, 0, 1, 1, 1, 1],
        [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    ],
    dtype=np.uint8,
)

SOLUTION_SEG_DEFORM = np.array(
    [
        [1, 1, 0, 0, 0, 0, 1, 1, 0, 0],
        [1, 0, 0, 1, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 1, 1, 1, 1],
        [0, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 1, 1, 1, 1],
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    ],
    dtype=np.uint8,
)

IMG_DEFORM = np.array(
    [
        [0.38570797, 0.60111725, 0.36168993, 0.9766824 , 0.9804071 ,
         0.16504207, 0.773007  , 0.16396737, 0.74197924, 0.5834533],
        [0.64376414, 0.8600482 , 0.6409536 , 0.7907393 , 0.12295883,
         0.13718218, 0.799585  , 0.21815887, 0.18057445, 0.14009792],
        [0.5858362 , 0.87031555, 0.9685376 , 0.4582324 , 0.62097746,
         0.7643881 , 0.40027583, 0.98094827, 0.6091135 , 0.25239545],
        [0.7894852 , 0.12621544, 0.70211643, 0.95580107, 0.78273964,
         0.46334684, 0.68930393, 0.14324893, 0.48638418, 0.44193688],
        [0.24136384, 0.544594  , 0.25968033, 0.20166956, 0.39456   ,
         0.7101957 , 0.5569414 , 0.44246438, 0.50165313, 0.29557464],
        [0.02714541, 0.96875787, 0.34546882, 0.5657312 , 0.51589125,
         0.7170873 , 0.24119139, 0.03581174, 0.7673236 , 0.4913606],
        [0.8621105 , 0.44834518, 0.3429032 , 0.2927389 , 0.33871126,
         0.60047305, 0.24167483, 0.58939844, 0.66042435, 0.25263473],
        [0.3359523 , 0.9866632 , 0.77512974, 0.12417328, 0.80207574,
         0.9293133 , 0.34909457, 0.84527844, 0.15256153, 0.02717197],
        [0.8016987 , 0.89196664, 0.5440732 , 0.82698894, 0.63820523,
         0.56431276, 0.42398015, 0.52417207, 0.341381  , 0.08803088],
        [0.8509897 , 0.17797235, 0.49373174, 0.4172536 , 0.7725485 ,
         0.5225525 , 0.74236554, 0.8941857 , 0.66937697, 0.9004244]
    ],
    dtype=np.float32
)

SOLUTION_IMG_DEFORM = np.array(
    [
         [0.55781573, 0.55602074, 0.61510146, 0.6557216 , 0.74465233,
          0.34918025, 0.5464359 , 0.37783048, 0.48432204, 0.47539356],
         [0.6877119 , 0.6898401 , 0.7843227 , 0.7053852 , 0.45963874,
          0.3509417 , 0.55363756, 0.3307155 , 0.3227715 , 0.32047814],
         [0.6337552 , 0.626425  , 0.73799026, 0.7011833 , 0.61110955,
          0.5806361 , 0.61246854, 0.55657953, 0.32726687, 0.31669885],
         [0.45436853, 0.40696928, 0.50267434, 0.62965983, 0.61723924,
          0.5862777 , 0.43496594, 0.46038425, 0.42629418, 0.42583832],
         [0.45915467, 0.5387882 , 0.3721795 , 0.4445874 , 0.60764503,
          0.49658483, 0.38581604, 0.47679353, 0.4138604 , 0.41264886],
         [0.5786425 , 0.40900826, 0.38210243, 0.48448592, 0.5254293 ,
          0.29107365, 0.41074762, 0.57386464, 0.51452476, 0.51448786],
         [0.72913975, 0.44022354, 0.5186094 , 0.7176185 , 0.51598567,
          0.522325  , 0.5373555 , 0.3551787 , 0.3365073 , 0.34499905],
         [0.59652734, 0.65013295, 0.66612613, 0.61211884, 0.50271696,
          0.5658946 , 0.3489212 , 0.13374893, 0.12688974, 0.12811106],
         [0.53263193, 0.6313792 , 0.6409404 , 0.58373624, 0.6578029 ,
          0.6688923 , 0.515851  , 0.40555277, 0.36103463, 0.34474418],
         [0.54122925, 0.6448051 , 0.6286122 , 0.58842754, 0.67819464,
          0.70035094, 0.60202646, 0.60641575, 0.60643274, 0.60643274]
    ],
    dtype=np.float32
)
# fmt: on


def test_seg_weights_simple():
    classweights = (0.3, 0.7)
    w0 = 12.0
    sigma = 2.0
    weights = delta.data.seg_weights(
        MASK_1D, classweights=classweights, w0=w0, sigma=sigma
    )
    target = w0 * np.exp(-(DISTS_1D**2) / (2 * sigma**2))
    target[DISTS_1D == 0] = classweights[1]
    target[DISTS_1D != 0] += classweights[0]
    npt.assert_allclose(weights, target)


def test_seg_weights_complex():
    path = Path(__file__).parent / "data/images"
    mask = imgops.read_image(path / "complex_mask.png")
    target = imgops.read_image(path / "complex_weights.png")
    weights = delta.data.seg_weights(mask)
    norm_weights = weights / weights.max()
    int_weights = imgops.to_integer_values(norm_weights, np.uint8)
    npt.assert_allclose(int_weights / 255, target)


def test_seg_weights_2D_complex():  # noqa: N802
    path = Path(__file__).parent / "data/images"
    mask = imgops.read_image(path / "complex_mask.png")
    target = imgops.read_image(path / "complex_weights_2D.png")
    weights = delta.data.seg_weights_2D(mask, classweights=(0.3, 0.7))
    norm_weights = weights / weights.max()
    int_weights = imgops.to_integer_values(norm_weights, np.uint8)
    npt.assert_allclose(int_weights / 255, target)


def test_estimate_seg2D_classweights():  # noqa: N802
    rng = npr.default_rng(seed=0)
    path = delta.assets.download_training_set("2D", "seg")
    class1, class2 = data.estimate_seg2D_classweights(path / "seg", 10, rng)
    assert class1 == 1.0
    assert class2 == 0.6748469718766749


@pytest.mark.skipif(sys.version_info < (3, 13), reason="requires python3.13 or higher")
def test_smart_elastic_deform():
    img, seg = data.smart_elastic_deform(
        [IMG_DEFORM, SEG_DEFORM],
        orderlist=[1, 0],
        sigma=2,
        points=2,
        rng=np.random.default_rng(0),
    )

    assert seg.dtype == SEG_DEFORM.dtype
    assert img.dtype == IMG_DEFORM.dtype
    npt.assert_array_equal(seg, SOLUTION_SEG_DEFORM)
    npt.assert_array_equal(img, SOLUTION_IMG_DEFORM)
