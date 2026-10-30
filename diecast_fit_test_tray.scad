// Mini-Waymo micro: dimension-test tray ONLY.
// NOT a production chassis or verified match to any Waymo collectible.
// Open shell, measure usable interior, wheel wells, axle offsets and fastener mounts.
// Then update parameters before printing. Print at 100% scale.
inside_length_mm = 90; // PLACEHOLDER
inside_width_mm = 35;   // PLACEHOLDER
tray_clearance_mm = 0.7; // radial allowance all sides
floor_thickness_mm = 1.5;
edge_lip_height_mm = 2.0;
edge_lip_wall_mm = 1.0;
wheelbase_mm = 69.5; // placeholder if 1:43

length = inside_length_mm - 2*tray_clearance_mm;
width  = inside_width_mm - 2*tray_clearance_mm;
assert(length>30 && width>10,"Dimensions too small");
difference(){
 union(){
  translate([-length/2,-width/2,0])cube([length,width,floor_thickness_mm]);
  for(y=[-width/2,width/2-edge_lip_wall_mm])
    translate([-length/2,y,floor_thickness_mm])cube([length,edge_lip_wall_mm,edge_lip_height_mm]);
 }
 // No drive-shaft holes until measured; markers are shallow engraving.
 for(x=[-wheelbase_mm/2,wheelbase_mm/2])
   translate([x,0,floor_thickness_mm-0.35])cube([.6,width-3,.75],center=true);
}
