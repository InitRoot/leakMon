<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>Simple Leak Monitor</title>
    <!-- Favicon-->
    <link rel="icon" type="image/x-icon" href="assets/favicon.ico" />
    <!-- Core theme CSS (includes Bootstrap)-->
    <link href="css/styles.css" rel="stylesheet" />
</head>
<?php

?>
<body>
<!-- Responsive navbar-->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <!-- Logo Image -->
        <img src="assets/logo2.png" height="65" alt="" class="d-inline-block align-middle mr-2">
        <!-- Logo Text -->

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                <li class="nav-item"><a class="nav-link active" aria-current="page" href="#">Home</a></li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" id="navbarDropdown" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">Queries</a>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                        <li><a class="dropdown-item" href="?daily">Daily</a></li>
                        <li><a class="dropdown-item" href="?all">All</a></li>
                        <li><a class="dropdown-item" href="?unall">Unique Total</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </div>
</nav>
<!-- Page content-->
<?php
$valForTitle = "Test";
?>

<div class="container">
            <?php
            $myPDO = NULL;              //close db just in case...
            //open the database
            $myPDO = new PDO('sqlite:../db/osintDB.db');
            //throw exceptions
            $myPDO->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $query = NULL;


            if(isset($_GET['daily'])){
                $valForTitle = "Daily";
                dailyData();
            } elseif (isset($_GET['all'])) {
                $valForTitle = "All";
                allData();
            } elseif (isset($_GET['unall'])) {
                $valForTitle = "Unique All";
                allUnData();
            } else {
                $valForTitle = "Daily";
                dailyData();
            }
            function dailyData()
            {
                global $query, $myPDO;
                //SELECT * FROM (SELECT Link FROM tblData GROUP BY Link HAVING COUNT(Link) = X AND Current = X) AS ONLY_ONCE
                $query = $myPDO->prepare("SELECT * FROM (SELECT * FROM tblData GROUP BY Link HAVING COUNT(Link) = 1 AND Current = 'X') AS ONLY_ONCE order by DateDisc DESC");
            }
            function allData()
            {
                global $query, $myPDO;
                //SELECT * FROM (SELECT Link FROM tblData GROUP BY Link HAVING COUNT(Link) = X AND Current = X) AS ONLY_ONCE
                $query = $myPDO->prepare("SELECT * FROM tblData order by DateDisc DESC LIMIT 450");
            }

            function allUnData()
            {
                global $query, $myPDO;
                //SELECT * FROM (SELECT Link FROM tblData GROUP BY Link HAVING COUNT(Link) = X AND Current = X) AS ONLY_ONCE
                $query = $myPDO->prepare("SELECT * from (select *, row_number() over (partition by link order by DateDisc) as RowNbr from tblData) source where RowNbr = 1 order by DateDisc DESC LIMIT 450");

            }

            ?>
                <div class="text-center mt-5">
        <h1> <?php echo $valForTitle?> Links</h1>

    <p class="lead"><em>A simple script that monitors data leaks by @initroot.</em></p>
</div>
<br/>
<table class="table table-hover">
    <thead>
    <tr>
        <th scope="col">URL</th>
        <th scope="col">Date Seen</th>
        <th scope="col">Source</th>
    </tr>
    </thead>
    <tbody>
    <?php
            $query->execute();
            while($fetch = $query->fetch()){
                ?>
                <tr>
                    <td>
                        <a href="<?php echo $fetch['Link']?>"><?php echo $fetch['Link']?></a>
                    </td>
                    <td><?php echo $fetch['DateDisc']?></td>
                    <td><?php echo $fetch['Source']?></td>
                </tr>

                <?php
            }
            ?>
            </tbody>
        </table>
</div>
<!-- Bootstrap core JS-->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.bundle.min.js"></script>
<!-- Core theme JS-->
<script src="js/scripts.js"></script>
</body>
</html>
